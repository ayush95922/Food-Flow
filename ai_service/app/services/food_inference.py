"""Shared preprocessing + inference code for the Food-101 MobileNetV2 classifier.

This file is the SINGLE SOURCE OF TRUTH for image preprocessing. The training
pipeline, the evaluation code, predict_food() and a future FastAPI service all
import `to_model_input` from here, so preprocessing cannot silently differ.
"""
import io
import json
import os

import numpy as np
import tensorflow as tf
from PIL import Image, ImageOps

IMG_SIZE = 224
ALLOWED_EXTENSIONS = {".jpg", ".jpeg", ".png", ".bmp", ".webp", ".gif"}
ALLOWED_PIL_FORMATS = {"JPEG", "PNG", "BMP", "WEBP", "GIF"}
MAX_FILE_BYTES = 10 * 1024 * 1024
MIN_SIDE_PIXELS = 32
MODEL_FILENAME = "food_classifier_best.keras"

DISCLAIMER = ("Food-type classification from a photo only. It does not measure food "
              "quantity, freshness, remaining usable time, or food safety.")
CONFIDENCE_NOTE = ("Confidence is a raw softmax score, not a calibrated probability "
                   "that the prediction is correct.")


def to_model_input(image):
    """HxWx3 image (values 0-255, any dtype) -> uint8 tensor (IMG_SIZE, IMG_SIZE, 3).

    Steps: cast to float -> bilinear resize with antialiasing -> round -> clip -> uint8.
    The model itself rescales 0..255 -> -1..1 (MobileNetV2 convention) in its first layer.
    """
    image = tf.convert_to_tensor(image)
    image = tf.cast(image, tf.float32)
    image = tf.image.resize(image, (IMG_SIZE, IMG_SIZE), method="bilinear", antialias=True)
    image = tf.clip_by_value(tf.round(image), 0.0, 255.0)
    image = tf.cast(image, tf.uint8)
    image.set_shape([IMG_SIZE, IMG_SIZE, 3])
    return image


class ImageValidationError(Exception):
    """Raised for any input problem. `code` is machine-readable, `message` is safe to show."""

    def __init__(self, code, message):
        super().__init__(message)
        self.code = code
        self.message = message


def decode_image_bytes(data, max_bytes=MAX_FILE_BYTES):
    """Validate raw bytes and return an RGB uint8 numpy array (H, W, 3)."""
    if not isinstance(data, (bytes, bytearray)) or len(data) == 0:
        raise ImageValidationError("EMPTY_FILE", "The file is empty.")
    if len(data) > max_bytes:
        raise ImageValidationError(
            "FILE_TOO_LARGE", "File exceeds the %d MB limit." % (max_bytes // (1024 * 1024)))
    try:
        with Image.open(io.BytesIO(data)) as probe:
            fmt = probe.format
            probe.verify()  # cheap integrity check; invalidates `probe`
        if fmt not in ALLOWED_PIL_FORMATS:
            raise ImageValidationError("UNSUPPORTED_FILE_TYPE", "Unsupported image format.")
        with Image.open(io.BytesIO(data)) as img:
            img = ImageOps.exif_transpose(img)  # honour phone-camera rotation
            img = img.convert("RGB")            # handles grayscale / RGBA / palette images
            arr = np.array(img, dtype=np.uint8)
    except ImageValidationError:
        raise
    except Exception:
        raise ImageValidationError("INVALID_IMAGE", "The file is not a readable image.") from None
    if arr.ndim != 3 or arr.shape[2] != 3 or min(arr.shape[:2]) < MIN_SIDE_PIXELS:
        raise ImageValidationError(
            "IMAGE_TOO_SMALL",
            "Image must be at least %dx%d pixels." % (MIN_SIDE_PIXELS, MIN_SIDE_PIXELS))
    return arr


def load_image_as_rgb_array(path, max_bytes=MAX_FILE_BYTES):
    """Validate a local file path and return an RGB uint8 numpy array."""
    try:
        path = os.fspath(path)
    except TypeError:
        raise ImageValidationError("INVALID_PATH", "Invalid file path.") from None
    if not os.path.isfile(path):
        raise ImageValidationError("FILE_NOT_FOUND", "File not found.")
    if os.path.splitext(path)[1].lower() not in ALLOWED_EXTENSIONS:
        raise ImageValidationError(
            "UNSUPPORTED_FILE_TYPE",
            "Unsupported file extension. Allowed: " + ", ".join(sorted(ALLOWED_EXTENSIONS)))
    try:
        with open(path, "rb") as f:
            data = f.read(max_bytes + 1)
    except OSError:
        raise ImageValidationError("FILE_UNREADABLE", "The file could not be read.") from None
    return decode_image_bytes(data, max_bytes)


def decide_uncertain(sorted_top_probs, conf_threshold, margin_threshold):
    """Return (needs_manual_verification, reasons) from the top probabilities (descending)."""
    top1 = float(sorted_top_probs[0])
    margin = top1 - float(sorted_top_probs[1]) if len(sorted_top_probs) > 1 else top1
    reasons = []
    if top1 < conf_threshold:
        reasons.append("low_confidence")
    if margin < margin_threshold:
        reasons.append("small_margin_between_top2")
    return len(reasons) > 0, reasons


def error_result(code, message):
    return {
        "status": "error",
        "error_code": code,
        "error_message": message,
        "needs_manual_verification": True,
    }


def apply_manual_correction(result, corrected_food, corrected_category=None,
                            corrected_donation_category=None):
    """Return a copy of a prediction result with the donor's correction recorded.

    `corrected_food` may be ANY text: the donor is not limited to the 101 Food-101 classes.
    """
    out = dict(result)
    out["user_correction"] = {
        "food": str(corrected_food).strip(),
        "category": corrected_category or result.get("food_category"),
        "donation_category": corrected_donation_category or result.get("donation_category"),
    }
    out["needs_manual_verification"] = False
    out["verified_by_donor"] = True
    return out


class FoodRecognizer:
    """Wraps a trained Keras model + labels + category mapping + uncertainty rules."""

    def __init__(self, model, class_names, category_map=None, config=None,
                 conf_threshold=0.5, margin_threshold=0.10, top_k=3):
        n_out = int(model.output_shape[-1])
        if n_out != len(class_names):
            raise ValueError("Model has %d outputs but %d class names were given."
                             % (n_out, len(class_names)))
        self.model = model
        self.class_names = list(class_names)
        self.category_map = category_map if category_map is not None else {}
        self.config = config or {}
        self.conf_threshold = float(conf_threshold)
        self.margin_threshold = float(margin_threshold)
        self.top_k = min(int(top_k), len(self.class_names))

    @classmethod
    def from_dir(cls, artifact_dir, model_filename=MODEL_FILENAME):
        def _load(name, default):
            p = os.path.join(artifact_dir, name)
            if os.path.isfile(p):
                with open(p, "r", encoding="utf-8") as f:
                    return json.load(f)
            return default

        class_names = _load("class_labels.json", None)["classes"]
        category_map = _load("food_category_mapping.json", {})
        config = _load("model_config.json", {})
        unc = config.get("uncertainty", {})
        model = tf.keras.models.load_model(os.path.join(artifact_dir, model_filename),
                                           compile=False)
        return cls(model, class_names, category_map, config,
                   conf_threshold=unc.get("conf_threshold", 0.5),
                   margin_threshold=unc.get("margin_threshold", 0.10))

    # ---- public API -------------------------------------------------------
    def predict(self, image_path, conf_threshold=None, margin_threshold=None):
        return self._run(lambda: load_image_as_rgb_array(image_path),
                         conf_threshold, margin_threshold)

    def predict_bytes(self, data, conf_threshold=None, margin_threshold=None):
        """Same as predict() but for uploaded bytes (useful for a web API; no file path)."""
        return self._run(lambda: decode_image_bytes(data),
                         conf_threshold, margin_threshold)

    def predict_array(self, rgb_array, conf_threshold=None, margin_threshold=None):
        x = to_model_input(rgb_array)                     # SAME function as training
        x = tf.cast(x, tf.float32)[tf.newaxis, ...]
        probs = self.model(x, training=False).numpy()[0]
        return self._format(probs, conf_threshold, margin_threshold)

    # ---- internals --------------------------------------------------------
    def _run(self, loader, conf_threshold, margin_threshold):
        try:
            arr = loader()
        except ImageValidationError as e:
            return error_result(e.code, e.message)
        except Exception:
            return error_result("INTERNAL_ERROR", "The image could not be processed.")
        try:
            return self.predict_array(arr, conf_threshold, margin_threshold)
        except Exception:
            return error_result("INFERENCE_ERROR", "Prediction failed.")

    def _category(self, label):
        entry = self.category_map.get(label)
        if entry is None:
            return "unmapped", "unmapped", True
        return (entry.get("category", "unmapped"), entry.get("donation_category", "unmapped"),
                bool(entry.get("needs_review", True)))

    def _format(self, probs, conf_threshold, margin_threshold):
        ct = self.conf_threshold if conf_threshold is None else float(conf_threshold)
        mt = self.margin_threshold if margin_threshold is None else float(margin_threshold)
        order = np.argsort(-probs)[: self.top_k]
        top_probs = [float(probs[i]) for i in order]
        uncertain, reasons = decide_uncertain(top_probs, ct, mt)
        best_label = self.class_names[int(order[0])]
        category, donation_category, cat_review = self._category(best_label)
        return {
            "status": "ok",
            "predicted_label": best_label,
            "predicted_food": best_label.replace("_", " "),
            "food_category": category,
            "donation_category": donation_category,
            "category_needs_review": cat_review,
            "confidence": round(top_probs[0], 4),
            "top_predictions": [
                {"label": self.class_names[int(i)],
                 "display_name": self.class_names[int(i)].replace("_", " "),
                 "confidence": round(float(probs[i]), 4)}
                for i in order
            ],
            "needs_manual_verification": bool(uncertain),
            "uncertainty_reasons": reasons,
            "confidence_note": CONFIDENCE_NOTE,
            "disclaimer": DISCLAIMER,
        }