"""Matching service: converts API schemas to algorithm objects and back. No HTTP logic here."""
from copy import deepcopy
from typing import Dict, List

from app.algorithms import dynamic_matching as dm
from app.algorithms import nearest_recipient as nr
from app.algorithms import rule_based as rb
from app.algorithms.explain import build_explanation, rejection_text
from app.algorithms.matching_core import MatchingOptions, TravelModel
from app.algorithms.models import Candidate, Donation, Recipient
from app.schemas.matching import MatchingRequest
from app.utils.categories import normalize_category
from app.utils.errors import ValidationFailed

ASSUMPTIONS = [
    "Travel distance/time are SIMULATED: haversine x detour factor / assumed speed (no real road data).",
    "Collection model: the recipient's team travels to the donor (pickup ETA) and brings the food back (delivery ETA).",
    "Hard constraints: availability, accepted category, unmet demand > 0, capacity > 0, service radius, pickup deadline, estimated usable time.",
    "The dynamic strategy is a hand-weighted multi-criteria scoring model, not a trained ML model.",
    "Donations in one request are processed sequentially by (urgency desc, pickup deadline asc); state carries over.",
]


def to_donation(d) -> Donation:
    return Donation(d.id, normalize_category(d.food_category), d.quantity, d.location.t(),
                    d.pickup_deadline_minutes, d.remaining_usable_minutes, d.urgency)


def to_recipient(r) -> Recipient:
    return Recipient(r.id, r.name, r.location.t(), r.demand_remaining, r.capacity,
                     [normalize_category(c) for c in r.accepted_categories] or ["any"], r.available,
                     r.available_in_minutes, r.historical_received, r.allocation_count, r.priority)


def _cand_out(c: Candidate, rank=None) -> dict:
    return {"recipient_id": c.recipient_id, "recipient_name": c.recipient_name, "rank": rank, "feasible": c.feasible,
            "total_score": round(c.total_score, 4) if c.feasible else None,
            "factor_scores": {k: round(v, 4) for k, v in c.factor_scores.items()},
            "weighted_contributions": {k: round(v, 4) for k, v in c.weighted_contributions.items()},
            "distance_km": round(c.distance_km, 3), "pickup_eta_minutes": round(c.pickup_eta_min, 1),
            "delivery_eta_minutes": round(c.delivery_eta_min, 1), "acceptable_quantity": round(c.acceptable_qty, 2),
            "rejection_codes": c.rejection_reasons, "rejection_reasons": rejection_text(c.rejection_reasons)}


def _run(strategy: str, donations: List[Donation], recipients: List[Recipient], opts: MatchingOptions, weights,
         top_n: int, include_rejected: bool) -> Dict:
    recs: Dict[str, Recipient] = {r.id: deepcopy(r) for r in recipients}
    order = sorted(donations, key=lambda d: (-d.urgency_value(), d.pickup_deadline_min, d.id))
    results, total, allocated = [], 0.0, 0.0
    for d in order:
        if strategy == "nearest":
            res = nr.allocate(d, list(recs.values()), opts, explain=build_explanation)
        elif strategy == "rule_based":
            res = rb.allocate(d, list(recs.values()), opts, explain=build_explanation)
        else:
            res = dm.allocate(d, list(recs.values()), opts, weights, explain=build_explanation)
        got = 0.0
        for a in res.allocations:
            r = recs[a.recipient_id]
            r.demand_remaining -= a.quantity
            r.capacity -= a.quantity
            r.allocation_count += 1
            r.historical_received += a.quantity
            got += a.quantity
        total += d.quantity
        allocated += got
        feas = [c for c in res.candidates if c.feasible]
        rej = [c for c in res.candidates if not c.feasible]
        status = "unallocated" if got <= 1e-9 else "fully_allocated" if res.unallocated_qty <= 1e-6 else "partially_allocated"
        results.append({
            "donation_id": d.id, "status": status, "unallocated_quantity": round(res.unallocated_qty, 4),
            "allocations": [{"recipient_id": a.recipient_id, "recipient_name": a.recipient_name, "quantity": round(a.quantity, 4),
                             "distance_km": round(a.distance_km, 3), "pickup_eta_minutes": round(a.pickup_eta_min, 1),
                             "delivery_eta_minutes": round(a.delivery_eta_min, 1), "score": round(a.score, 4),
                             "chunk": a.rank, "explanation": a.explanation} for a in res.allocations],
            "ranked_candidates": [_cand_out(c, i + 1) for i, c in enumerate(feas[:top_n])],
            "rejected_candidates": [_cand_out(c) for c in rej] if include_rejected else []})
    return {"order": [d.id for d in order], "results": results, "recipients": recs,
            "summary": {"total_quantity": total, "allocated_quantity": allocated, "unallocated_quantity": total - allocated,
                        "allocation_rate": allocated / total if total else 0.0}}


def recommend(req: MatchingRequest) -> Dict:
    o = req.options
    opts = MatchingOptions(max_radius_km=o.max_radius_km, max_chunks=o.max_chunks,
                           travel=TravelModel(o.speed_kmph, o.detour_factor))
    try:
        weights = dm.Weights.from_dict(req.weights.model_dump(exclude_none=True)) if req.weights else dm.Weights()
        norm = weights.normalized()
    except ValueError as e:
        raise ValidationFailed(str(e))
    donations = [to_donation(d) for d in req.donations]
    recipients = [to_recipient(r) for r in req.recipients]
    main = _run(req.strategy, donations, recipients, opts, weights, o.top_n, o.include_rejected)
    comparison = None
    if req.compare_strategies:
        comparison = {}
        for s in ("nearest", "rule_based", "dynamic"):
            r = _run(s, donations, recipients, opts, weights, 1, False)
            comparison[s] = {"summary": r["summary"],
                             "plan": [{"donation_id": x["donation_id"], "recipient_id": a["recipient_id"], "quantity": a["quantity"],
                                       "distance_km": a["distance_km"]} for x in r["results"] for a in x["allocations"]]}
    states = [{"recipient_id": r.id, "demand_remaining": round(r.demand_remaining, 4), "capacity": round(r.capacity, 4),
               "historical_received": round(r.historical_received, 4), "allocation_count": r.allocation_count}
              for r in main["recipients"].values()]
    return {"strategy": req.strategy, "weights_used": norm if req.strategy == "dynamic" else None,
            "processing_order": main["order"], "results": main["results"], "summary": main["summary"],
            "updated_recipient_states": states, "comparison": comparison, "assumptions": ASSUMPTIONS}
