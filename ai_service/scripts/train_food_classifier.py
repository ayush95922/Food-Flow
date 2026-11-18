"""Train / evaluate / export the Food-101 MobileNetV2 classifier (same logic as notebooks/food_recognition.ipynb).

Real training (Colab GPU):   python scripts/train_food_classifier.py --out-dir /content/food_model_artifacts
Pipeline check WITHOUT data: python scripts/train_food_classifier.py --smoke-synthetic --weights none --out-dir /tmp/food_smoke
   (random synthetic images - proves the train/export/inference plumbing only; the metrics are MEANINGLESS)
Artifacts written: food_classifier_best.keras, class_labels.json, food_category_mapping.json, model_config.json,
evaluation.json, per_class_metrics.csv, confusion_matrix.npy.  Copy them to saved_models/food_classifier/.
"""
import argparse
import json
import shutil
import sys
import time
from pathlib import Path

import numpy as np

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))

import tensorflow as tf  # noqa: E402
from sklearn.metrics import accuracy_score, classification_report, confusion_matrix, f1_score, precision_recall_fscore_support  # noqa: E402
from sklearn.model_selection import train_test_split  # noqa: E402
from tensorflow import keras  # noqa: E402

from app.services.food_inference import to_model_input  # noqa: E402
from app.services.food_model import build_model, choose_thresholds, unfreeze_top  # noqa: E402

CLASS_NAMES = json.loads((ROOT / "app/utils/food101_class_names_reference.json").read_text())["classes"]


def synthetic_data(n_per_class, n_classes, seed=0):
    rng = np.random.default_rng(seed)
    X, y = [], []
    for c in range(n_classes):
        base = rng.integers(0, 255, 3)
        for _ in range(n_per_class):
            img = np.clip(base + rng.normal(0, 40, (224, 224, 3)), 0, 255).astype("uint8")
            X.append(img)
            y.append(c)
    return np.array(X), np.array(y)


def food101_data(batch, val_fraction, seed):
    import tensorflow_datasets as tfds
    (tr, te), info = tfds.load("food101", split=["train", "validation"], shuffle_files=False, with_info=True,
                               decoders={"image": tfds.decode.SkipDecoding()})   # TFDS 'validation' == official TEST split
    names = info.features["label"].names
    labels = np.concatenate([b.numpy() for b in tr.map(lambda e: e["label"]).batch(4096)])
    idx_tr, idx_va = train_test_split(np.arange(len(labels)), test_size=val_fraction, stratify=labels, random_state=seed)
    def subset(ds, idx):
        mask = tf.constant(np.isin(np.arange(len(labels)), idx))
        return ds.enumerate().filter(lambda i, e: tf.gather(mask, i)).map(lambda i, e: e)
    def prep(ds, shuffle):
        ds = ds.map(lambda e: (to_model_input(tf.io.decode_image(e["image"], channels=3, expand_animations=False)), e["label"]),
                    num_parallel_calls=tf.data.AUTOTUNE)
        if shuffle:
            ds = ds.shuffle(1000, seed=seed)
        return ds.batch(batch).map(lambda x, y: (tf.cast(x, tf.float32), y)).prefetch(tf.data.AUTOTUNE)
    test_labels = np.concatenate([b.numpy() for b in te.map(lambda e: e["label"]).batch(4096)])
    return names, prep(subset(tr, idx_tr), True), prep(subset(tr, idx_va), False).cache(), prep(te, False), labels[idx_va], test_labels


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--out-dir", required=True)
    ap.add_argument("--smoke-synthetic", action="store_true")
    ap.add_argument("--weights", default="imagenet", choices=["imagenet", "none"])
    ap.add_argument("--head-epochs", type=int, default=5)
    ap.add_argument("--ft-epochs", type=int, default=10)
    ap.add_argument("--batch", type=int, default=64)
    ap.add_argument("--seed", type=int, default=42)
    a = ap.parse_args()
    out = Path(a.out_dir)
    out.mkdir(parents=True, exist_ok=True)
    tf.keras.utils.set_random_seed(a.seed)

    if a.smoke_synthetic:
        names = CLASS_NAMES
        X, y = synthetic_data(6, len(names), a.seed)
        Xtr, Xva, ytr, yva = train_test_split(X, y, test_size=0.2, stratify=y, random_state=a.seed)
        Xva, Xte, yva, yte = train_test_split(Xva, yva, test_size=0.5, random_state=a.seed)
        mk = lambda X, y, sh: tf.data.Dataset.from_tensor_slices((X.astype("float32"), y)).shuffle(256).batch(16) if sh else \
            tf.data.Dataset.from_tensor_slices((X.astype("float32"), y)).batch(16)
        train_ds, val_ds, test_ds, val_labels, test_labels = mk(Xtr, ytr, True), mk(Xva, yva, False), mk(Xte, yte, False), yva, yte
    else:
        names, train_ds, val_ds, test_ds, val_labels, test_labels = food101_data(a.batch, 0.10, a.seed)
    assert len(names) == 101

    model = build_model(len(names), weights=None if a.weights == "none" else "imagenet")
    ck = out / "checkpoints"; ck.mkdir(exist_ok=True)
    cb = lambda p: [keras.callbacks.EarlyStopping("val_loss", patience=3, restore_best_weights=True),
                    keras.callbacks.ModelCheckpoint(str(p), monitor="val_loss", save_best_only=True),
                    keras.callbacks.ReduceLROnPlateau("val_loss", factor=0.5, patience=1, min_lr=1e-6)]
    model.compile(keras.optimizers.Adam(1e-3), "sparse_categorical_crossentropy", metrics=["accuracy"])
    t0 = time.time()
    h1 = model.fit(train_ds, validation_data=val_ds, epochs=a.head_epochs, callbacks=cb(ck / "head.keras"), verbose=2).history
    model = keras.models.load_model(ck / "head.keras")
    unfreeze_top(model, 100)
    model.compile(keras.optimizers.Adam(1e-5), "sparse_categorical_crossentropy", metrics=["accuracy"])
    h2 = model.fit(train_ds, validation_data=val_ds, epochs=a.ft_epochs, callbacks=cb(ck / "finetuned.keras"), verbose=2).history
    cands = {n: keras.models.load_model(ck / f"{n}.keras") for n in ("head", "finetuned")}
    vl = {n: m.evaluate(val_ds, verbose=0)[0] for n, m in cands.items()}
    sel = min(vl, key=vl.get)
    best = cands[sel]
    best.save(out / "food_classifier_best.keras")

    vp = best.predict(val_ds, verbose=0)
    thr, how, table = choose_thresholds(vp, val_labels)
    tp = best.predict(test_ds, verbose=0)
    yt, yp = test_labels[:len(tp)], tp.argmax(1)
    labels = np.arange(len(names))
    pm, rm, fm, _ = precision_recall_fscore_support(yt, yp, labels=labels, average="macro", zero_division=0)
    ev = {"smoke_synthetic_NOT_MEANINGFUL": bool(a.smoke_synthetic), "selected_model": sel, "validation_loss": vl,
          "n_test": int(len(yt)), "accuracy": float(accuracy_score(yt, yp)),
          "top3_accuracy": float((np.argsort(-tp, 1)[:, :3] == yt[:, None]).any(1).mean()),
          "macro_precision": float(pm), "macro_recall": float(rm), "macro_f1": float(fm),
          "weighted_f1": float(f1_score(yt, yp, labels=labels, average="weighted", zero_division=0)),
          "train_minutes": round((time.time() - t0) / 60, 2)}
    rep = classification_report(yt, yp, labels=labels, target_names=names, output_dict=True, zero_division=0)
    import pandas as pd
    pd.DataFrame([{"class": c, **{k: rep[c][k] for k in ("precision", "recall", "f1-score", "support")}} for c in names]).to_csv(out / "per_class_metrics.csv", index=False)
    np.save(out / "confusion_matrix.npy", confusion_matrix(yt, yp, labels=labels))
    (out / "evaluation.json").write_text(json.dumps(ev, indent=2))
    (out / "class_labels.json").write_text(json.dumps({"classes": names}, indent=2))
    shutil.copy(ROOT / "saved_models/food_classifier/food_category_mapping.json", out / "food_category_mapping.json")
    (out / "model_config.json").write_text(json.dumps({
        "architecture": "MobileNetV2 transfer learning, input 224x224x3 (0..255), Rescaling inside model",
        "uncertainty": {"conf_threshold": thr, "margin_threshold": 0.10, "how_chosen": how,
                        "rule": "needs_manual_verification if top1 < conf_threshold OR (top1 - top2) < margin_threshold"},
        "validation_threshold_table": table, "smoke_synthetic_NOT_MEANINGFUL": bool(a.smoke_synthetic),
        "limitations": ["Food-type classification only: no quantity, freshness or food-safety inference.",
                        "Food-101 has only 101 (mostly Western) classes; many local dishes are not covered.",
                        "Softmax confidence is not a calibrated probability."]}, indent=2))
    print(json.dumps(ev, indent=2))


if __name__ == "__main__":
    main()
