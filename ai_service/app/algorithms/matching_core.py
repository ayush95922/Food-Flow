"""Shared machinery for the three matching strategies.

Travel model (SIMULATED, documented assumption):
    road_km      = haversine(donor, recipient) * detour_factor
    travel_min   = road_km / speed_kmph * 60
Collection model: the recipient (or its volunteer) becomes free after `available_in_min`,
travels to the donor (pickup_eta) and brings the food back (delivery_eta).
    pickup_eta   = available_in_min + travel_min
    delivery_eta = pickup_eta + travel_min

Hard feasibility constraints (an allocation is rejected if any fails):
    H1 recipient available            H4 acceptable quantity > 0
    H2 category accepted              H5 pickup_eta   <= pickup_deadline
    H3 demand_remaining > 0           H6 delivery_eta <= remaining_usable_time
Ablation switches can disable H6 (usable time) and the capacity cap on H4.
"""
from copy import copy
from dataclasses import dataclass, field
from typing import Callable, Dict, List, Optional

from app.algorithms.models import Allocation, AllocationResult, Candidate, Donation, Recipient
from app.utils.geo import haversine_km, travel_minutes


@dataclass
class TravelModel:
    speed_kmph: float = 25.0
    detour_factor: float = 1.3

    def distance_km(self, a, b) -> float:
        return haversine_km(a, b) * self.detour_factor

    def minutes(self, km: float) -> float:
        return travel_minutes(km, self.speed_kmph)


@dataclass
class MatchingOptions:
    max_radius_km: float = 15.0
    enforce_usable_time: bool = True
    enforce_capacity: bool = True
    enforce_pickup_deadline: bool = True
    max_chunks: int = 3                  # a donation may be split across at most this many recipients
    min_chunk: float = 1.0               # do not create allocations smaller than this
    travel: TravelModel = field(default_factory=TravelModel)


def evaluate_candidates(d: Donation, recipients: List[Recipient], opts: MatchingOptions,
                        qty_needed: Optional[float] = None) -> List[Candidate]:
    """Compute distance/ETA/feasibility for every recipient (no scoring yet)."""
    q = d.quantity if qty_needed is None else qty_needed
    out = []
    for r in recipients:
        km = opts.travel.distance_km(d.location, r.location)
        t = opts.travel.minutes(km)
        pickup = max(0.0, r.available_in_min) + t
        delivery = pickup + t
        acc = r.acceptable_qty(opts.enforce_capacity)
        reasons = []
        if not r.available:
            reasons.append("recipient_unavailable")
        if r.accepts(d.category) == 0.0:
            reasons.append("category_not_accepted")
        if r.demand_remaining <= 0:
            reasons.append("no_remaining_demand")
        elif opts.enforce_capacity and r.capacity <= 0:
            reasons.append("no_receiving_capacity")
        if km > opts.max_radius_km:
            reasons.append("outside_service_radius")
        if opts.enforce_pickup_deadline and pickup > d.pickup_deadline_min:
            reasons.append("pickup_deadline_missed")
        if opts.enforce_usable_time and delivery > d.remaining_usable_min:
            reasons.append("usable_time_exceeded")
        if acc < min(opts.min_chunk, q) and not reasons:
            reasons.append("quantity_below_minimum")
        out.append(Candidate(recipient_id=r.id, recipient_name=r.name, feasible=not reasons,
                             rejection_reasons=reasons, distance_km=km, pickup_eta_min=pickup,
                             delivery_eta_min=delivery, acceptable_qty=acc,
                             proposed_qty=min(q, acc) if not reasons else 0.0))
    return out


def _clip(x: float) -> float:
    return 0.0 if x < 0 else 1.0 if x > 1 else x


def basic_scores(c: Candidate, d: Donation, r: Recipient, opts: MatchingOptions, max_demand: float,
                 qty: float) -> Dict[str, float]:
    """Factor scores shared by the rule-based and proposed strategies (all in [0, 1])."""
    return {
        "demand": _clip(r.demand_remaining / max_demand) if max_demand > 0 else 0.0,
        "quantity": _clip(min(qty, c.acceptable_qty) / qty) if qty > 0 else 0.0,
        "distance": _clip(1.0 - c.distance_km / opts.max_radius_km),
    }


# A ranker takes (donation, feasible candidates, recipients_by_id, opts, qty) and fills
# candidate.factor_scores / weighted_contributions / total_score, returning them sorted best-first.
Ranker = Callable[[Donation, List[Candidate], Dict[str, Recipient], MatchingOptions, float], List[Candidate]]


def allocate_donation(strategy_name: str, ranker: Ranker, d: Donation, recipients: List[Recipient],
                      opts: MatchingOptions, explain: Optional[Callable] = None) -> AllocationResult:
    """Allocate a donation greedily over up to `max_chunks` recipients, re-ranking after each chunk
    with the remaining quantity and the reduced demand/capacity of already-chosen recipients.
    Never allocates more than the donation quantity or more than a recipient can accept."""
    work = {r.id: copy(r) for r in recipients}
    remaining = float(d.quantity)
    allocations: List[Allocation] = []
    first_pass: List[Candidate] = []

    for chunk in range(opts.max_chunks):
        if remaining < min(opts.min_chunk, d.quantity) - 1e-9:
            break
        cands = evaluate_candidates(d, list(work.values()), opts, qty_needed=remaining)
        feas = [c for c in cands if c.feasible]
        ranked = ranker(d, feas, work, opts, remaining) if feas else []
        if chunk == 0:
            first_pass = ranked + [c for c in cands if not c.feasible]
        if not ranked:
            break
        best = ranked[0]
        take = min(remaining, best.acceptable_qty)
        best.proposed_qty = take
        r = work[best.recipient_id]
        alloc = Allocation(d.id, r.id, r.name, round(take, 6), best.distance_km, best.pickup_eta_min,
                           best.delivery_eta_min, best.total_score, strategy_name, rank=chunk + 1)
        if explain is not None:
            alloc.explanation = explain(d, best, ranked, remaining)
        allocations.append(alloc)
        remaining -= take
        r.demand_remaining -= take
        if opts.enforce_capacity:
            r.capacity -= take
        r.allocation_count += 1
        r.historical_received += take
    return AllocationResult(d.id, strategy_name, allocations, max(0.0, remaining), first_pass)
