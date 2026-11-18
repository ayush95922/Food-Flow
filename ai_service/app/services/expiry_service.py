"""Inference for the remaining-usable-time regressor (experimental estimate, not a safety check)."""
from functools import lru_cache
import json
from pathlib import Path
from typing import Dict, Optional

import joblib
import numpy as np
import pandas as pd

from app.config import get_settings
from app.services import expiry_training as T
from app.utils.errors import ModelNotAvailable, ValidationFailed


class UsableTimeEstimator:
    def __init__(self, pipeline, meta: Dict):
        self.pipeline, self.meta = pipeline, meta

    @classmethod
    def from_dir(cls, d: Path) -> "UsableTimeEstimator":
        mp, jp = d / T.MODEL_FILE, d / T.META_FILE
        if not mp.is_file() or not jp.is_file():
            raise ModelNotAvailable(f"Usable-time model not found in {d}. Run `python scripts/train_usable_time.py`.")
        return cls(joblib.load(mp), json.loads(jp.read_text()))

    def predict(self, food_category: str, elapsed_minutes: float, storage_condition: str,
                temperature_c: Optional[float] = None, packaging: Optional[str] = None) -> Dict:
        if food_category not in T.BASE_LIFE_H:
            raise ValidationFailed(f"Unknown food_category '{food_category}'. Allowed: {sorted(T.BASE_LIFE_H)}")
        if storage_condition not in T.STORAGE_FACTOR:
            raise ValidationFailed(f"Unknown storage_condition '{storage_condition}'. Allowed: {sorted(T.STORAGE_FACTOR)}")
        if packaging is not None and packaging not in T.PACKAGING_FACTOR:
            raise ValidationFailed(f"Unknown packaging '{packaging}'. Allowed: {sorted(T.PACKAGING_FACTOR)}")
        if elapsed_minutes < 0:
            raise ValidationFailed("elapsed_minutes must be >= 0")
        raw = pd.DataFrame([{"food_category": food_category, "storage_condition": storage_condition,
                             "packaging": packaging, "temperature_c": temperature_c,
                             "elapsed_h": elapsed_minutes / 60.0}])
        used_defaults = [k for k, v in (("temperature_c", temperature_c), ("packaging", packaging)) if v is None]
        X = T.engineer(raw)[T.NUM_FEATURES + T.CAT_FEATURES]
        hours = float(max(0.0, self.pipeline.predict(X)[0]))
        half = float(self.meta["interval_halfwidth_h_q90"])
        notes = ["Estimate comes from a model trained on SYNTHETIC data; real-world error is unknown."]
        if used_defaults:
            notes.append("Missing inputs replaced by defaults: " + ", ".join(used_defaults))
        if elapsed_minutes / 60.0 > T.BASE_LIFE_H[food_category] * 2.5:
            notes.append("Elapsed time is far beyond the typical range seen in training; treat as unreliable.")
        level = "high" if half > 0.75 * max(hours, 1e-6) or hours < 1.0 else "medium" if half > 0.35 * max(hours, 1e-6) else "lower"
        return {
            "estimated_remaining_minutes": round(hours * 60, 1),
            "conservative_remaining_minutes": round(max(0.0, hours - half) * 60, 1),
            "interval_minutes": [round(max(0.0, hours - half) * 60, 1), round((hours + half) * 60, 1)],
            "uncertainty_level": level,
            "model": self.meta["selected_model"],
            "data_source": self.meta["data_source"],
            "notes": notes,
            "disclaimer": T.DISCLAIMER,
        }


@lru_cache
def get_estimator() -> UsableTimeEstimator:
    return UsableTimeEstimator.from_dir(get_settings().resolve(get_settings().usable_time_model_dir))


def estimate_from_request(req) -> Dict:
    from datetime import datetime, timezone
    from app.utils.categories import normalize_category
    if req.elapsed_minutes is not None:
        elapsed = req.elapsed_minutes
    else:
        now = req.current_time or datetime.now(req.prepared_at.tzinfo or timezone.utc)
        elapsed = (now - req.prepared_at).total_seconds() / 60.0
        if elapsed < 0:
            raise ValidationFailed("prepared_at is in the future")
    out = get_estimator().predict(normalize_category(req.food_category), elapsed, req.storage_condition,
                                  req.temperature_c, req.packaging)
    out["elapsed_minutes_used"] = round(elapsed, 1)
    if req.food_type:
        out["notes"].append("food_type is informational; the estimate is driven by food_category.")
    return out
