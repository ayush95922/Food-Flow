"""Explanations generated ONLY from actual algorithm outputs (factor scores, constraints, quantities)."""
from typing import Dict, List

from app.algorithms.matching_core import Candidate

HIGH, LOW = 0.70, 0.30

_REASON_TEXT = {
    "recipient_unavailable": "recipient is currently unavailable",
    "category_not_accepted": "recipient does not accept this food category",
    "no_remaining_demand": "recipient has no remaining unmet demand",
    "no_receiving_capacity": "recipient has no receiving capacity left",
    "outside_service_radius": "recipient is outside the service radius",
    "pickup_deadline_missed": "food cannot be collected before the pickup deadline",
    "usable_time_exceeded": "food would not arrive within its estimated usable time",
    "quantity_below_minimum": "acceptable quantity is below the minimum chunk",
}


def rejection_text(codes: List[str]) -> List[str]:
    return [_REASON_TEXT.get(c, c) for c in codes]


def _phrase(factor: str, score: float, c: Candidate, d, qty: float) -> str:
    pct = f"{score:.2f}"
    return {
        "demand": f"High unmet demand relative to other candidates (score {pct})",
        "quantity": f"Can take {min(qty, c.acceptable_qty):.0f} of {qty:.0f} portions offered (score {pct})",
        "distance": f"Short travel distance, {c.distance_km:.1f} km simulated road distance (score {pct})",
        "urgency": f"Fast pickup for urgent food, pickup ETA {c.pickup_eta_min:.0f} min (score {pct})",
        "usable_time": f"Food arrives with a comfortable margin before estimated expiry, delivery ETA "
                       f"{c.delivery_eta_min:.0f} min (score {pct})",
        "capacity": f"Sufficient receiving capacity (score {pct})",
        "compatibility": f"Food category matches the recipient's accepted categories (score {pct})",
        "pickup_feasibility": f"Pickup can be completed well before the donor deadline (score {pct})",
        "fairness": f"Lower historical allocation than other candidates (score {pct})",
    }.get(factor, f"{factor} score {pct}")


def build_explanation(d, best: Candidate, ranked: List[Candidate], qty: float) -> Dict:
    """Return strengths (scores >= 0.7), weaknesses (<= 0.3), top contributors and a runner-up comparison."""
    scores = best.factor_scores
    strengths = [_phrase(k, v, best, d, qty) for k, v in sorted(scores.items(), key=lambda kv: -kv[1]) if v >= HIGH]
    weaknesses = [f"Low {k.replace('_', ' ')} score ({v:.2f})" for k, v in scores.items() if v <= LOW]
    top = sorted(best.weighted_contributions.items(), key=lambda kv: -kv[1])[:3]
    out = {
        "recommended_recipient": best.recipient_name,
        "total_score": round(best.total_score, 4),
        "reasons": strengths or ["No single factor scored >= 0.70; recipient chosen as best overall trade-off"],
        "weaknesses": weaknesses,
        "top_weighted_factors": [{"factor": k, "contribution": round(v, 4)} for k, v in top],
        "factor_scores": {k: round(v, 4) for k, v in scores.items()},
        "hard_constraints_passed": ["available", "category accepted", "demand > 0", "pickup deadline", "usable time"],
    }
    if len(ranked) > 1:
        ru = ranked[1]
        gaps = {k: best.factor_scores.get(k, 0) - ru.factor_scores.get(k, 0) for k in best.factor_scores}
        lead = max(gaps.items(), key=lambda kv: kv[1])
        out["runner_up"] = {"recipient": ru.recipient_name, "score": round(ru.total_score, 4),
                            "largest_advantage_of_recommended": {"factor": lead[0], "difference": round(lead[1], 4)}}
    return out
