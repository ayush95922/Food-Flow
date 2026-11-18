"""Remaining-usable-time estimation: SYNTHETIC research dataset + model training.

!!! IMPORTANT - READ BEFORE USING THE NUMBERS !!!
No public, real, labelled dataset of "remaining usable hours of donated cooked food" is known to the
authors. The data below is therefore SYNTHETIC, generated from a documented *assumption model*:

    usable_life_h = base_life_h[category] * 2 ** ((T_ref - T) / 10)   # temperature acceleration (Q10-style, assumed)
                    * storage_factor[storage] * packaging_factor[packaging] * noise
    remaining_h   = max(0, usable_life_h - elapsed_h)

* base_life_h values are conservative ASSUMPTIONS inspired by the general "2-hour / 4-hour" cooked-food
  guidance and typical refrigerated shelf-life tables; they are NOT validated food-safety limits.
* The ML models learn this synthetic generator. High R2 therefore shows that the pipeline works; it says
  NOTHING about accuracy on real food. Validate against real, expert-labelled data before any use.
* This module is an experimental ESTIMATE. It is not a food-safety certification and never confirms that
  food is safe to eat.
"""
import json
import time
from pathlib import Path
from typing import Dict, List, Tuple

import joblib
import numpy as np
import pandas as pd
from sklearn.compose import ColumnTransformer
from sklearn.ensemble import GradientBoostingRegressor, RandomForestRegressor
from sklearn.impute import SimpleImputer
from sklearn.linear_model import LinearRegression
from sklearn.metrics import mean_absolute_error, mean_squared_error, r2_score
from sklearn.model_selection import train_test_split
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import OneHotEncoder, StandardScaler

# ----------------------------- documented assumptions -----------------------------------------
BASE_LIFE_H = {            # hours of usable life at the reference temperature (T_REF), ASSUMED
    "cooked_meal": 6.0, "cooked_protein_meal": 4.0, "fresh_salad": 4.0, "soup_liquid": 6.0,
    "ready_to_eat_snack": 8.0, "bakery_dry": 36.0, "sweets_desserts": 24.0,
}
T_REF = 20.0
STORAGE_FACTOR = {"room_temp": 1.0, "refrigerated": 3.0, "frozen": 10.0, "hot_holding": 1.5, "insulated_box": 1.3}
PACKAGING_FACTOR = {"open": 0.8, "covered": 1.0, "sealed_container": 1.2, "vacuum_sealed": 1.5}
STORAGE_DEFAULT_TEMP = {"room_temp": 25.0, "refrigerated": 4.0, "frozen": -18.0, "hot_holding": 60.0, "insulated_box": 30.0}

NUM_FEATURES = ["elapsed_h", "temperature_c", "hours_since_prep_to_now_ratio"]
CAT_FEATURES = ["food_category", "storage_condition", "packaging"]
TARGET = "remaining_usable_h"
MODEL_FILE = "usable_time_model.joblib"
META_FILE = "usable_time_meta.json"

DISCLAIMER = ("Experimental estimate trained on SYNTHETIC data generated from documented assumptions. "
              "It is not a food-safety certification and does not confirm that food is safe to eat. "
              "Always follow local food-safety rules and the donor's/recipient's own checks.")


def generate_synthetic_dataset(n: int = 6000, seed: int = 42) -> pd.DataFrame:
    rng = np.random.default_rng(seed)
    cats = rng.choice(list(BASE_LIFE_H), n)
    storage = rng.choice(list(STORAGE_FACTOR), n, p=[0.35, 0.25, 0.03, 0.17, 0.20])
    pack = rng.choice(list(PACKAGING_FACTOR), n, p=[0.1, 0.35, 0.4, 0.15])
    temp = np.array([STORAGE_DEFAULT_TEMP[s] for s in storage]) + rng.normal(0, 2.5, n)
    life = (np.array([BASE_LIFE_H[c] for c in cats]) * 2.0 ** ((T_REF - np.clip(temp, -20, 70)) / 10.0)
            * np.array([STORAGE_FACTOR[s] for s in storage]) * np.array([PACKAGING_FACTOR[p] for p in pack])
            * rng.lognormal(0, 0.15, n))
    life = np.clip(life, 0.5, 72.0)                      # cap: nothing is assumed usable beyond 72 h
    elapsed = rng.uniform(0, 1.2, n) * np.minimum(life, 24.0)
    df = pd.DataFrame({"food_category": cats, "storage_condition": storage, "packaging": pack,
                       "temperature_c": temp.round(1), "elapsed_h": elapsed.round(2)})
    df[TARGET] = np.maximum(0.0, life - elapsed).round(3)
    # introduce 3 % missing temperature / packaging to exercise the imputation path
    m1, m2 = rng.random(n) < 0.03, rng.random(n) < 0.03
    df.loc[m1, "temperature_c"] = np.nan
    df.loc[m2, "packaging"] = np.nan
    return df


def engineer(df: pd.DataFrame) -> pd.DataFrame:
    """Feature engineering shared by training and inference."""
    out = df.copy()
    default_t = out["storage_condition"].map(STORAGE_DEFAULT_TEMP)
    out["temperature_c"] = out["temperature_c"].fillna(default_t)           # missing temp -> storage default
    out["packaging"] = out["packaging"].fillna("covered")                   # missing packaging -> neutral
    out["hours_since_prep_to_now_ratio"] = out["elapsed_h"] / out["food_category"].map(BASE_LIFE_H).fillna(6.0)
    return out


def _preprocessor():
    return ColumnTransformer([
        ("num", Pipeline([("imp", SimpleImputer(strategy="median")), ("sc", StandardScaler())]), NUM_FEATURES),
        ("cat", Pipeline([("imp", SimpleImputer(strategy="most_frequent")),
                          ("oh", OneHotEncoder(handle_unknown="ignore"))]), CAT_FEATURES),
    ])


def candidate_models(seed: int = 42) -> Dict[str, object]:
    return {
        "linear_regression": LinearRegression(),
        "random_forest": RandomForestRegressor(n_estimators=150, min_samples_leaf=2, n_jobs=1, random_state=seed),
        "gradient_boosting": GradientBoostingRegressor(n_estimators=250, max_depth=3, learning_rate=0.08, random_state=seed),
    }


def _metrics(y, p) -> Dict[str, float]:
    return {"MAE_h": float(mean_absolute_error(y, p)), "RMSE_h": float(np.sqrt(mean_squared_error(y, p))),
            "R2": float(r2_score(y, p))}


def train_and_save(out_dir: str, n: int = 6000, seed: int = 42) -> Dict:
    """Train all candidates, select by VALIDATION RMSE, report TEST metrics once, save best pipeline."""
    out = Path(out_dir)
    out.mkdir(parents=True, exist_ok=True)
    df = engineer(generate_synthetic_dataset(n, seed))
    X, y = df[NUM_FEATURES + CAT_FEATURES], df[TARGET]
    X_tr, X_tmp, y_tr, y_tmp = train_test_split(X, y, test_size=0.3, random_state=seed)
    X_va, X_te, y_va, y_te = train_test_split(X_tmp, y_tmp, test_size=0.5, random_state=seed)
    results, fitted = {}, {}
    for name, est in candidate_models(seed).items():
        pipe = Pipeline([("prep", _preprocessor()), ("model", est)])
        t0 = time.time()
        pipe.fit(X_tr, y_tr)
        results[name] = {"validation": _metrics(y_va, np.maximum(0, pipe.predict(X_va))),
                         "fit_seconds": round(time.time() - t0, 2)}
        fitted[name] = pipe
    best = min(results, key=lambda k: results[k]["validation"]["RMSE_h"])
    for name, pipe in fitted.items():
        results[name]["test"] = _metrics(y_te, np.maximum(0, pipe.predict(X_te)))
    resid = np.abs(y_va - np.maximum(0, fitted[best].predict(X_va)))
    meta = {
        "data_source": "SYNTHETIC (documented assumption model) - NOT real data", "n_rows": int(n), "seed": seed,
        "split": {"train": len(X_tr), "validation": len(X_va), "test": len(X_te)},
        "selected_model": best, "selection_rule": "lowest validation RMSE",
        "results": results, "interval_halfwidth_h_q90": float(np.quantile(resid, 0.90)),
        "interval_note": "90th percentile of absolute validation residuals; synthetic-data based, so NOT a guaranteed coverage on real food",
        "assumptions": {"BASE_LIFE_H": BASE_LIFE_H, "T_REF_C": T_REF, "STORAGE_FACTOR": STORAGE_FACTOR,
                        "PACKAGING_FACTOR": PACKAGING_FACTOR, "temperature_rule": "life x 2^((T_ref - T)/10), assumed",
                        "noise": "lognormal(0, 0.15)"},
        "features": {"numeric": NUM_FEATURES, "categorical": CAT_FEATURES},
        "disclaimer": DISCLAIMER,
    }
    joblib.dump(fitted[best], out / MODEL_FILE)
    (out / META_FILE).write_text(json.dumps(meta, indent=2))
    return meta
