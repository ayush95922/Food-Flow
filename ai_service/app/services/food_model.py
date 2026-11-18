"""Model definition (MobileNetV2 transfer learning) shared by the training script and tests.
Identical architecture to the notebook: augmentation (train only) -> Rescaling(-1..1) -> MobileNetV2 -> GAP -> Dropout -> Dense softmax."""
import numpy as np
from tensorflow import keras
from tensorflow.keras import layers

IMG_SIZE = 224


def build_augmentation():
    return keras.Sequential([layers.RandomFlip("horizontal"), layers.RandomRotation(0.05),
                             layers.RandomZoom(0.1), layers.RandomContrast(0.1)], name="augmentation")


def build_model(num_classes=101, img_size=IMG_SIZE, dropout=0.3, weights="imagenet"):
    inputs = keras.Input(shape=(img_size, img_size, 3), name="image")
    x = build_augmentation()(inputs)
    x = layers.Rescaling(1.0 / 127.5, offset=-1.0, name="preprocess_rescale")(x)
    backbone = keras.applications.MobileNetV2(input_shape=(img_size, img_size, 3), include_top=False, weights=weights)
    backbone.trainable = False
    x = backbone(x, training=False)
    x = layers.GlobalAveragePooling2D(name="global_avg_pool")(x)
    x = layers.Dropout(dropout, name="dropout")(x)
    outputs = layers.Dense(num_classes, activation="softmax", name="food_probs")(x)
    return keras.Model(inputs, outputs, name="food101_mobilenetv2")


def get_backbone(m):
    for l in m.layers:
        if isinstance(l, keras.Model) and l.name.startswith("mobilenetv2"):
            return l
    raise ValueError("MobileNetV2 backbone not found")


def unfreeze_top(model, fine_tune_at=100):
    bb = get_backbone(model)
    bb.trainable = True
    for l in bb.layers[:fine_tune_at]:
        l.trainable = False
    for l in bb.layers:
        if isinstance(l, layers.BatchNormalization):
            l.trainable = False


def choose_thresholds(val_probs, val_labels, target_acc=0.90, margin=0.10):
    """Smallest confidence threshold whose accepted predictions reach target_acc on VALIDATION data."""
    top1 = val_probs.max(1)
    correct = val_probs.argmax(1) == val_labels
    rows = []
    for t in np.round(np.arange(0.05, 1.0, 0.05), 2):
        m = top1 >= t
        rows.append({"conf_threshold": float(t), "coverage": float(m.mean()),
                     "accepted_accuracy": float(correct[m].mean()) if m.any() else float("nan")})
    ok = [r for r in rows if r["coverage"] > 0 and r["accepted_accuracy"] >= target_acc]
    if ok:
        return ok[0]["conf_threshold"], "smallest validation threshold reaching target accuracy", rows
    return 0.5, "fallback 0.50 (no threshold reached the target accuracy)", rows
