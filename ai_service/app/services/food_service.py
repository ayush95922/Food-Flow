"""Food-image recognition service (lazy model loading + caching)."""
from functools import lru_cache
from pathlib import Path
from typing import Dict

from app.config import get_settings
from app.services.food_inference import MAX_FILE_BYTES, FoodRecognizer, apply_manual_correction
from app.utils.errors import AIServiceError, ModelNotAvailable

_STATUS = {"EMPTY_FILE": 400, "INVALID_IMAGE": 400, "IMAGE_TOO_SMALL": 400, "UNSUPPORTED_FILE_TYPE": 415,
           "FILE_TOO_LARGE": 413}


class ImageRejected(AIServiceError):
    pass


def model_dir() -> Path:
    s = get_settings()
    return s.resolve(s.food_model_dir)


def model_files_present() -> bool:
    d = model_dir()
    return (d / "food_classifier_best.keras").is_file() and (d / "class_labels.json").is_file()


@lru_cache
def get_recognizer() -> FoodRecognizer:
    if not model_files_present():
        raise ModelNotAvailable(
            "The food classifier has not been trained/installed. Train it with notebooks/food_recognition.ipynb on "
            f"Colab GPU and copy the exported artifacts into '{model_dir()}' (see README).")
    return FoodRecognizer.from_dir(str(model_dir()))




def _raise_image_error(res: Dict):
    code = res.get("error_code", "INTERNAL_ERROR")
    err = ImageRejected(res.get("error_message", "Image could not be processed"), code)
    err.status_code = _STATUS.get(code, 500)
    raise err


def recognize(data: bytes) -> Dict:
    """Backend selection (FOOD_BACKEND): local | groq | auto (local first, Groq as fallback when the local model
    is not installed, crashes, or - if GROQ_ON_UNCERTAIN=true - is unsure). Invalid images are rejected before
    any fallback, so bad uploads never reach Groq."""
    from app.services import groq_vision as gv
    mode = get_settings().food_backend.lower()
    res, local_error = None, None
    if mode in ("local", "auto"):
        try:
            res = get_recognizer().predict_bytes(data)
            if res.get("status") == "error":
                if res.get("error_code") in _STATUS:          # image problem -> same answer from any backend
                    _raise_image_error(res)
                local_error, res = AIServiceError(res.get("error_message", "Local model failed"), "LOCAL_MODEL_FAILED"), None
            else:
                res["source"] = "local_mobilenetv2"
        except ModelNotAvailable as e:
            local_error = e
        if mode == "local":
            if local_error:
                raise local_error
        elif res is not None and not (get_settings().groq_on_uncertain and res.get("needs_manual_verification")
                                      and gv.groq_configured()):
            res["manual_correction_allowed"] = True
            return res
    # Groq: explicit, or fallback
    if not gv.groq_configured():
        if local_error:
            raise ModelNotAvailable(local_error.message + " Alternatively set GROQ_API_KEY to use the Groq vision backend.")
        return res                                            # uncertain local result, no Groq available
    try:
        out = gv.recognize_with_groq(data)
    except AIServiceError:
        if res is not None:                                   # Groq failed but we have a local answer
            res["manual_correction_allowed"] = True
            return res
        raise
    if out.get("status") == "error":
        _raise_image_error(out)
    out["manual_correction_allowed"] = True
    if local_error:
        out["fallback_reason"] = local_error.message[:160]
    return out


def correct(result: Dict, food: str, category=None, donation_category=None) -> Dict:
    return apply_manual_correction(result, food, category, donation_category)
