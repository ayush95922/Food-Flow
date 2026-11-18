import pytest

from app.services import expiry_training as T
from app.services.expiry_service import get_estimator


def test_model_loads_and_predicts():
    r = get_estimator().predict("cooked_meal", 60, "room_temp", 25, "covered")
    assert r["estimated_remaining_minutes"] >= 0
    lo, hi = r["interval_minutes"]
    assert lo <= r["estimated_remaining_minutes"] <= hi
    assert "SYNTHETIC" in r["data_source"] and "not a food-safety certification" in r["disclaimer"]


def test_monotonic_in_elapsed_time():
    e = get_estimator()
    vals = [e.predict("cooked_meal", m, "room_temp", 25, "covered")["estimated_remaining_minutes"] for m in (0, 120, 240, 480)]
    assert vals[0] > vals[-1]


def test_refrigerated_outlasts_room_temp():
    e = get_estimator()
    a = e.predict("cooked_meal", 120, "refrigerated", 4, "covered")["estimated_remaining_minutes"]
    b = e.predict("cooked_meal", 120, "room_temp", 25, "covered")["estimated_remaining_minutes"]
    assert a > b


def test_missing_inputs_are_imputed_and_reported():
    r = get_estimator().predict("soup_liquid", 30, "refrigerated")
    assert any("Missing inputs" in n for n in r["notes"])


@pytest.mark.parametrize("kw", [dict(food_category="nope", elapsed_minutes=1, storage_condition="room_temp"),
                                dict(food_category="cooked_meal", elapsed_minutes=1, storage_condition="nope"),
                                dict(food_category="cooked_meal", elapsed_minutes=-5, storage_condition="room_temp")])
def test_invalid_inputs(kw):
    from app.utils.errors import ValidationFailed
    with pytest.raises(ValidationFailed):
        get_estimator().predict(kw["food_category"], kw["elapsed_minutes"], kw["storage_condition"])


def test_training_pipeline_metrics(tmp_path):
    meta = T.train_and_save(str(tmp_path), n=1500, seed=1)
    assert set(meta["results"]) == {"linear_regression", "random_forest", "gradient_boosting"}
    for r in meta["results"].values():
        assert {"MAE_h", "RMSE_h", "R2"} <= set(r["test"])
    assert meta["data_source"].startswith("SYNTHETIC")
    assert (tmp_path / T.MODEL_FILE).is_file()


def test_synthetic_dataset_has_missing_values_and_nonneg_target():
    df = T.generate_synthetic_dataset(800, 3)
    assert df["temperature_c"].isna().any() and (df[T.TARGET] >= 0).all()


def test_api(client):
    r = client.post("/api/ai/usable-time-estimation", json={"food_category": "meat_dish", "food_type": "steak", "elapsed_minutes": 45,
                                                              "storage_condition": "hot_holding"})
    assert r.status_code == 200 and r.json()["estimated_remaining_minutes"] >= 0   # dish category mapped
    bad = client.post("/api/ai/usable-time-estimation", json={"food_category": "cooked_meal", "storage_condition": "room_temp"})
    assert bad.status_code == 422 and bad.json()["error"]["code"] == "VALIDATION_ERROR"
    unk = client.post("/api/ai/usable-time-estimation", json={"food_category": "xyz", "elapsed_minutes": 5, "storage_condition": "room_temp"})
    assert unk.status_code == 422
