import numpy as np
import pandas as pd
import pytest

from app.services import forecasting_service as F


def test_insufficient_data_is_reported_not_fabricated():
    df = F.generate_synthetic_series(20)
    r = F.run_forecast(df.to_dict("records"), 7)
    assert r["status"] == "insufficient_data" and "forecast" not in r and "targets" not in r
    assert r["required_days"] == F.MIN_DAYS and "No forecast has been fabricated" in r["message"]
    assert F.run_forecast([], 7)["status"] == "insufficient_data"


@pytest.fixture(scope="module")
def result():
    return F.run_forecast(F.generate_synthetic_series(120).to_dict("records"), 7)


def test_forecast_shape_and_nonneg(result):
    assert result["status"] == "ok"
    for t in ("supply", "demand"):
        fc = result["targets"][t]["forecast"]
        assert len(fc) == 7 and all(f["forecast"] >= 0 and f["lower_90"] <= f["forecast"] <= f["upper_90"] for f in fc)
    assert len(result["imbalance"]) == 7


def test_time_based_split_and_metrics(result):
    ev = result["targets"]["demand"]["evaluation"]
    s = ev["splits"]
    assert s["train_days"] + s["validation_days"] + s["test_days"] == 120 and s["train_days"] > s["validation_days"]
    for name in ("naive_last", "moving_average_7", "linear_regression", "random_forest"):
        assert {"MAE", "RMSE", "sMAPE_pct", "MASE"} <= set(ev["results"][name]["test"])
    assert ev["selected_model"] in ev["results"]


def test_metrics_function():
    m = F.metrics([10, 20], [12, 18], 5.0)
    assert m["MAE"] == 2 and m["RMSE"] == pytest.approx(2) and m["MASE"] == pytest.approx(0.4)


def test_daily_aggregation_fills_gaps():
    df = pd.DataFrame({"date": ["2025-01-01", "2025-01-01", "2025-01-04"], "v": [1, 2, 5]})
    s = F.to_daily(df, "v")
    assert list(s.values) == [3, 0, 0, 5]


def test_category_forecast_and_api(client):
    recs = []
    base = F.generate_synthetic_series(100)
    for cat in ("cooked_meal", "bakery_dry"):
        for r in base.to_dict("records"):
            recs.append({"date": r["date"].date().isoformat(), "supply_qty": r["supply_qty"], "demand_qty": r["demand_qty"], "category": cat})
    recs += [{"date": "2025-01-01", "supply_qty": 1, "demand_qty": 1, "category": "tiny"}]
    j = client.post("/api/ai/forecast/demand", json={"records": recs, "horizon_days": 5}).json()
    assert j["status"] == "ok" and "cooked_meal" in j["category_demand"] and "tiny" in j["category_notes"]
    short = client.post("/api/ai/forecast/demand", json={"records": recs[:10]}).json()
    assert short["status"] == "insufficient_data"
    assert client.post("/api/ai/forecast/demand", json={"records": [], "horizon_days": 100}).status_code == 422
