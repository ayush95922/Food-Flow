"""Supply / demand forecasting pipeline.

DATA POLICY: the pipeline NEVER invents history. If fewer than `MIN_DAYS` days of real history are supplied
it returns status="insufficient_data" and states what is missing. `generate_synthetic_series` exists only for
tests/notebook demos and is labelled SYNTHETIC; no API endpoint uses it implicitly.

Protocol
  * daily aggregation (missing days are filled with 0 and counted in the report);
  * chronological split 70 % train / 15 % validation / 15 % test (no shuffling);
  * walk-forward evaluation in blocks of `EVAL_HORIZON` days (ML models are trained once on the data before the
    evaluated span; Holt-Winters is re-fitted per block); model chosen by validation MAE; test metrics reported
    for all models; the selected model is re-fitted on all data to forecast the requested horizon;
  * 90 % prediction band = forecast +/- 1.645 * validation-RMSE (rough, assumes roughly normal errors).
Metrics: MAE, RMSE, sMAPE and MASE (scaled by the in-sample one-step naive MAE).
"""
import warnings
from typing import Dict, List, Optional

import numpy as np
import pandas as pd
from sklearn.ensemble import RandomForestRegressor
from sklearn.linear_model import LinearRegression

MIN_DAYS = 56            # 8 weeks: >= ~39 train days + 8 val + 8 test, enough for weekly seasonality
EVAL_HORIZON = 7
LAGS_MIN = 14
SEASON = 7

REQUIREMENT_TEXT = (f"At least {MIN_DAYS} days of real, daily donation-supply and recipient-demand records are "
                    "required (more is better). Export them from the platform database (date, supply_qty, "
                    "demand_qty, optional category) and call the endpoint again. No forecast has been fabricated.")


# --------------------------------------------------------------------------- data
def generate_synthetic_series(days: int = 140, seed: int = 0, start: str = "2025-01-01") -> pd.DataFrame:
    """SYNTHETIC demo data (weekly seasonality + trend + noise). Never presented as real."""
    rng = np.random.default_rng(seed)
    idx = pd.date_range(start, periods=days, freq="D")
    dow = idx.dayofweek.values
    supply = 120 + 0.2 * np.arange(days) + 35 * (dow >= 4) + rng.normal(0, 12, days)
    demand = 150 + 0.1 * np.arange(days) + 20 * (dow == 6) + rng.normal(0, 15, days)
    return pd.DataFrame({"date": idx, "supply_qty": np.maximum(supply, 0).round(1),
                         "demand_qty": np.maximum(demand, 0).round(1), "category": "all", "data_source": "SYNTHETIC"})


def to_daily(df: pd.DataFrame, value_col: str) -> pd.Series:
    d = df.copy()
    d["date"] = pd.to_datetime(d["date"]).dt.normalize()
    s = d.groupby("date")[value_col].sum().sort_index()
    full = pd.date_range(s.index.min(), s.index.max(), freq="D")
    return s.reindex(full, fill_value=0.0).astype(float)


# --------------------------------------------------------------------------- metrics
def metrics(y, p, scale: float) -> Dict[str, float]:
    y, p = np.asarray(y, float), np.asarray(p, float)
    err = y - p
    denom = (np.abs(y) + np.abs(p)) / 2
    smape = float(np.mean(np.where(denom == 0, 0, np.abs(err) / np.where(denom == 0, 1, denom))) * 100)
    return {"MAE": float(np.mean(np.abs(err))), "RMSE": float(np.sqrt(np.mean(err ** 2))),
            "sMAPE_pct": smape, "MASE": float(np.mean(np.abs(err)) / scale) if scale > 0 else float("nan")}


# --------------------------------------------------------------------------- feature models
def _row(hist: List[float], t: int, date: pd.Timestamp) -> List[float]:
    dow = np.zeros(7)
    dow[date.dayofweek] = 1
    return [hist[t - 1], hist[t - 7], hist[t - 14], float(np.mean(hist[t - 7:t])), float(t), *dow]


def _fit_ml(kind: str, y: pd.Series, seed: int = 0):
    vals, idx = list(y.values), y.index
    X = [_row(vals, t, idx[t]) for t in range(LAGS_MIN, len(vals))]
    yy = vals[LAGS_MIN:]
    m = LinearRegression() if kind == "linear_regression" else RandomForestRegressor(
        n_estimators=200, min_samples_leaf=2, random_state=seed, n_jobs=1)
    m.fit(np.array(X), np.array(yy))
    return m


def _forecast_ml(model, y: pd.Series, h: int) -> np.ndarray:
    hist, out = list(y.values), []
    last = y.index[-1]
    for k in range(1, h + 1):
        d = last + pd.Timedelta(days=k)
        v = float(max(0.0, model.predict(np.array([_row(hist, len(hist), d)]))[0]))
        out.append(v)
        hist.append(v)
    return np.array(out)


def _forecast_baseline(kind: str, y: pd.Series, h: int) -> np.ndarray:
    v = y.values
    if kind == "moving_average_7":
        return np.repeat(v[-7:].mean(), h)
    if kind == "seasonal_naive_7":
        return np.array([v[-SEASON + (k % SEASON)] for k in range(h)])
    if kind == "naive_last":
        return np.repeat(v[-1], h)
    raise KeyError(kind)


def _forecast_hw(y: pd.Series, h: int) -> Optional[np.ndarray]:
    try:
        from statsmodels.tsa.holtwinters import ExponentialSmoothing
        with warnings.catch_warnings():
            warnings.simplefilter("ignore")
            fit = ExponentialSmoothing(y.values, trend="add", seasonal="add", seasonal_periods=SEASON).fit()
        return np.maximum(0.0, fit.forecast(h))
    except Exception:
        return None


MODELS = ["naive_last", "moving_average_7", "seasonal_naive_7", "linear_regression", "random_forest", "holt_winters"]


def _walk_forward(name: str, y: pd.Series, start: int, end: int, fitted=None) -> Optional[np.ndarray]:
    """Forecast y[start:end] in blocks of EVAL_HORIZON using only data before each block's origin."""
    preds = []
    for o in range(start, end, EVAL_HORIZON):
        h = min(EVAL_HORIZON, end - o)
        hist = y.iloc[:o]
        if name in ("linear_regression", "random_forest"):
            p = _forecast_ml(fitted, hist, h)
        elif name == "holt_winters":
            p = _forecast_hw(hist, h)
            if p is None:
                return None
        else:
            p = _forecast_baseline(name, hist, h)
        preds.append(p)
    return np.concatenate(preds)


def evaluate_models(y: pd.Series) -> Dict:
    n = len(y)
    n_tr, n_va = int(n * 0.70), int(n * 0.15)
    tr_end, va_end = n_tr, n_tr + n_va
    scale = float(np.mean(np.abs(np.diff(y.values[:tr_end])))) or 1.0
    res = {}
    for name in MODELS:
        fv = _fit_ml(name, y.iloc[:tr_end]) if name in ("linear_regression", "random_forest") else None
        pv = _walk_forward(name, y, tr_end, va_end, fv)
        if pv is None:
            res[name] = {"status": "unavailable (statsmodels missing or fit failed)"}
            continue
        ft = _fit_ml(name, y.iloc[:va_end]) if fv is not None else None
        pt = _walk_forward(name, y, va_end, n, ft)
        res[name] = {"validation": metrics(y.values[tr_end:va_end], pv, scale),
                     "test": metrics(y.values[va_end:], pt, scale), "_val_rmse": metrics(y.values[tr_end:va_end], pv, scale)["RMSE"]}
    ok = {k: v for k, v in res.items() if "validation" in v}
    best = min(ok, key=lambda k: ok[k]["validation"]["MAE"])
    return {"splits": {"train_days": tr_end, "validation_days": va_end - tr_end, "test_days": n - va_end},
            "results": res, "selected_model": best, "selection_rule": "lowest validation MAE"}


def forecast_series(y: pd.Series, horizon: int) -> Dict:
    ev = evaluate_models(y)
    best = ev["selected_model"]
    if best in ("linear_regression", "random_forest"):
        pred = _forecast_ml(_fit_ml(best, y), y, horizon)
    elif best == "holt_winters":
        pred = _forecast_hw(y, horizon)
    else:
        pred = _forecast_baseline(best, y, horizon)
    rmse = ev["results"][best]["validation"]["RMSE"]
    dates = [(y.index[-1] + pd.Timedelta(days=k)).strftime("%Y-%m-%d") for k in range(1, horizon + 1)]
    forecast = [{"date": d, "forecast": round(float(p), 2), "lower_90": round(max(0.0, float(p) - 1.645 * rmse), 2),
                 "upper_90": round(float(p) + 1.645 * rmse, 2)} for d, p in zip(dates, pred)]
    for v in ev["results"].values():
        v.pop("_val_rmse", None)
    return {"selected_model": best, "evaluation": ev, "forecast": forecast}


def run_forecast(records: List[Dict], horizon_days: int = 7, by_category: bool = True) -> Dict:
    """records: dicts with date, supply_qty, demand_qty and optional category."""
    df = pd.DataFrame(records)
    base = {"data_source": "caller-provided history", "horizon_days": horizon_days}
    if df.empty or not {"date", "supply_qty", "demand_qty"} <= set(df.columns):
        return {**base, "status": "insufficient_data", "n_days": 0, "required_days": MIN_DAYS,
                "message": REQUIREMENT_TEXT}
    df["date"] = pd.to_datetime(df["date"])
    n_days = int((df["date"].max() - df["date"].min()).days) + 1
    if n_days < MIN_DAYS:
        return {**base, "status": "insufficient_data", "n_days": n_days, "required_days": MIN_DAYS,
                "message": REQUIREMENT_TEXT}
    out = {**base, "status": "ok", "n_days": n_days, "targets": {}, "category_demand": {}, "category_notes": {},
           "limitations": ["Forecasts are statistical extrapolations of the supplied history; they cannot anticipate "
                           "events not present in the data (holidays, disasters, policy changes).",
                           "Prediction bands are rough (validation-RMSE based)."]}
    total_s, total_d = to_daily(df, "supply_qty"), to_daily(df, "demand_qty")
    out["filled_missing_days"] = int((total_s.reindex(pd.date_range(total_s.index.min(), total_s.index.max())).isna()).sum())
    fs, fd = forecast_series(total_s, horizon_days), forecast_series(total_d, horizon_days)
    out["targets"] = {"supply": fs, "demand": fd}
    out["imbalance"] = [{"date": a["date"], "expected_demand_minus_supply": round(b["forecast"] - a["forecast"], 2),
                         "direction": "shortage_of_supply" if b["forecast"] > a["forecast"] else "surplus_of_supply"}
                        for a, b in zip(fs["forecast"], fd["forecast"])]
    if by_category and "category" in df.columns and df["category"].nunique() > 1:
        for cat, g in df.groupby("category"):
            span = int((g["date"].max() - g["date"].min()).days) + 1
            if span < MIN_DAYS:
                out["category_notes"][str(cat)] = f"insufficient_data ({span} < {MIN_DAYS} days)"
                continue
            out["category_demand"][str(cat)] = forecast_series(to_daily(g, "demand_qty"), horizon_days)
    return out
