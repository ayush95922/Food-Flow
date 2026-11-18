"""Shared fixtures. NOTE: the food-recognition tests build an UNTRAINED (random-weight) MobileNetV2 model.
They verify software behaviour (loading, shapes, validation, output schema) - NOT model accuracy."""
import io
import json
import os
import sys
from pathlib import Path

os.environ.setdefault("TF_CPP_MIN_LOG_LEVEL", "3")
ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))

import numpy as np
import pytest
from PIL import Image


def png_bytes(w=300, h=200, seed=0, mode="RGB"):
    arr = np.random.default_rng(seed).integers(0, 255, (h, w, 3), dtype=np.uint8)
    buf = io.BytesIO()
    Image.fromarray(arr).convert(mode).save(buf, format="PNG")
    return buf.getvalue()


@pytest.fixture(scope="session")
def food_dir(tmp_path_factory):
    from app.services.food_model import build_model
    d = tmp_path_factory.mktemp("food_model")
    names = json.loads((ROOT / "app/utils/food101_class_names_reference.json").read_text())["classes"]
    model = build_model(len(names), weights=None)
    model.save(d / "food_classifier_best.keras")
    (d / "class_labels.json").write_text(json.dumps({"classes": names}))
    (d / "food_category_mapping.json").write_text((ROOT / "saved_models/food_classifier/food_category_mapping.json").read_text())
    (d / "model_config.json").write_text(json.dumps({"uncertainty": {"conf_threshold": 0.5, "margin_threshold": 0.1}}))
    return d


@pytest.fixture(scope="session")
def recognizer(food_dir):
    from app.services.food_inference import FoodRecognizer
    return FoodRecognizer.from_dir(str(food_dir))


@pytest.fixture()
def client():
    from fastapi.testclient import TestClient
    from app.main import app
    return TestClient(app)


@pytest.fixture()
def client_with_model(client, recognizer, monkeypatch):
    from app.services import food_service
    monkeypatch.setattr(food_service, "get_recognizer", lambda: recognizer)
    return client
