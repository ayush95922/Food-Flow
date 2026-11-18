"""Evaluation metrics for allocation experiments."""
from typing import Dict, List

import numpy as np

from app.algorithms.fairness_optimizer import jain_index


def summarize_run(donated: float, delivered_by_recipient: Dict[str, float], initial_demand: Dict[str, float],
                  transport_km_weighted: float, delivered_total: float, matching_time_s: float,
                  computational_time_s: float, n_donations: int, extra: Dict = None) -> Dict[str, float]:
    served = [r for r, v in delivered_by_recipient.items() if v > 1e-9]
    ratios = [min(1.0, delivered_by_recipient.get(r, 0.0) / d) for r, d in initial_demand.items() if d > 0]
    unmet = sum(max(0.0, d - delivered_by_recipient.get(r, 0.0)) for r, d in initial_demand.items())
    out = {
        "total_donated": donated,
        "redistributed": delivered_total,
        "potential_wastage": max(0.0, donated - delivered_total),
        "wastage_pct": 100.0 * max(0.0, donated - delivered_total) / donated if donated else 0.0,
        "unmet_demand": unmet,
        "beneficiaries_served": delivered_total,                 # 1 portion = 1 beneficiary meal (assumption)
        "recipients_served": float(len(served)),
        "avg_transport_km": transport_km_weighted / delivered_total if delivered_total > 0 else 0.0,
        "jain_fairness": jain_index(ratios),
        "matching_time_ms_per_donation": 1000.0 * matching_time_s / max(n_donations, 1),
        "matching_time_total_s": matching_time_s,
        "computational_time_s": computational_time_s,
    }
    if extra:
        out.update(extra)
    return out


def aggregate(rows: List[Dict[str, float]]) -> Dict[str, Dict[str, float]]:
    keys = rows[0].keys()
    return {k: {"mean": float(np.mean([r[k] for r in rows])), "std": float(np.std([r[k] for r in rows], ddof=1)) if len(rows) > 1 else 0.0}
            for k in keys}
