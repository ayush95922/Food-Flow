import numpy as np
import pytest

from tests.conftest import png_bytes
from app.services.food_inference import apply_manual_correction, decide_uncertain, to_model_input


def test_model_loading_and_class_count(recognizer):
    assert len(recognizer.class_names) == 101
    assert recognizer.model.output_shape[-1] == 101
    assert recognizer.category_map["pizza"]["donation_category"] == "ready_to_eat_snack"


def test_inference_output_schema(recognizer):
    r = recognizer.predict_bytes(png_bytes())
    assert r["status"] == "ok"
    top = r["top_predictions"]
    assert len(top) == 3
    confs = [t["confidence"] for t in top]
    assert confs == sorted(confs, reverse=True)
    assert all(0.0 <= c <= 1.0 for c in confs) and sum(confs) <= 1.0001
    assert r["predicted_label"] == top[0]["label"] and r["confidence"] == confs[0]
    assert r["food_category"] != "" and "donation_category" in r
    assert isinstance(r["needs_manual_verification"], bool)
    assert "does not measure food quantity" in r["disclaimer"]


def test_untrained_model_is_flagged_uncertain(recognizer):
    # random weights -> near-uniform softmax -> must be flagged for manual verification
    assert recognizer.predict_bytes(png_bytes(seed=3))["needs_manual_verification"] is True


@pytest.mark.parametrize("data,code", [(b"", "EMPTY_FILE"), (b"not an image", "INVALID_IMAGE"),
                                       (png_bytes(10, 10), "IMAGE_TOO_SMALL")])
def test_invalid_images_fail_safely(recognizer, data, code):
    r = recognizer.predict_bytes(data)
    assert r["status"] == "error" and r["error_code"] == code and r["needs_manual_verification"] is True


def test_file_too_large(recognizer):
    from app.services.food_inference import decode_image_bytes, ImageValidationError
    with pytest.raises(ImageValidationError) as e:
        decode_image_bytes(b"0" * 100, max_bytes=50)
    assert e.value.code == "FILE_TOO_LARGE"


def test_preprocessing_shape_and_dtype():
    x = to_model_input(np.zeros((77, 130, 3), dtype=np.uint8))
    assert tuple(x.shape) == (224, 224, 3) and x.dtype.name == "uint8"


def test_grayscale_and_rgba_accepted(recognizer):
    assert recognizer.predict_bytes(png_bytes(mode="L"))["status"] == "ok"
    assert recognizer.predict_bytes(png_bytes(mode="RGBA"))["status"] == "ok"


def test_uncertainty_rule():
    assert decide_uncertain([0.9, 0.05], 0.5, 0.1) == (False, [])
    assert decide_uncertain([0.4, 0.05], 0.5, 0.1)[1] == ["low_confidence"]
    assert "small_margin_between_top2" in decide_uncertain([0.6, 0.55], 0.5, 0.1)[1]


def test_manual_correction_is_free_text(recognizer):
    r = recognizer.predict_bytes(png_bytes())
    c = apply_manual_correction(r, "Paneer butter masala", None, "cooked_meal")
    assert c["user_correction"]["food"] == "Paneer butter masala" and c["verified_by_donor"] and not c["needs_manual_verification"]
    assert c["user_correction"]["donation_category"] == "cooked_meal"


def test_category_mapping_complete():
    import json
    from tests.conftest import ROOT
    m = json.loads((ROOT / "saved_models/food_classifier/food_category_mapping.json").read_text())
    names = json.loads((ROOT / "app/utils/food101_class_names_reference.json").read_text())["classes"]
    assert set(m) == set(names) and len(m) == 101
    assert all("donation_category" in v and v["donation_category"] != "unmapped" for v in m.values())


# ------------------------------------------------------------------ API
def test_api_food_recognition_ok(client_with_model):
    r = client_with_model.post("/api/ai/food-recognition", files={"file": ("a.png", png_bytes(), "image/png")})
    assert r.status_code == 200 and len(r.json()["top_predictions"]) == 3


def test_api_invalid_image_400(client_with_model):
    r = client_with_model.post("/api/ai/food-recognition", files={"file": ("a.png", b"garbage", "image/png")})
    assert r.status_code == 400 and r.json()["error"]["code"] == "INVALID_IMAGE"


def test_api_wrong_content_type_415(client_with_model):
    r = client_with_model.post("/api/ai/food-recognition", files={"file": ("a.txt", b"hello", "text/plain")})
    assert r.status_code == 415


def test_api_too_large_413(client_with_model, monkeypatch):
    from app.config import Settings
    import app.api.food_recognition as fr
    monkeypatch.setattr(fr, "get_settings", lambda: Settings(max_upload_mb=0))
    r = client_with_model.post("/api/ai/food-recognition", files={"file": ("a.png", png_bytes(), "image/png")})
    assert r.status_code == 413


def test_api_model_not_installed_503(client, monkeypatch):
    from app.services import food_service
    monkeypatch.setattr(food_service, "model_files_present", lambda: False)
    food_service.get_recognizer.cache_clear()
    r = client.post("/api/ai/food-recognition", files={"file": ("a.png", png_bytes(), "image/png")})
    assert r.status_code == 503 and r.json()["error"]["code"] == "MODEL_NOT_AVAILABLE"


def test_api_manual_correction(client):
    orig = {"status": "ok", "predicted_food": "pizza", "food_category": "pizza", "needs_manual_verification": True}
    r = client.post("/api/ai/food-recognition/correct", json={"original_result": orig, "corrected_food": "veg pulao"})
    assert r.status_code == 200 and r.json()["verified_by_donor"] is True
