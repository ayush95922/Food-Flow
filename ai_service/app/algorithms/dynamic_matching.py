"""Strategy C - Proposed Dynamic Multi-Factor Matching (a configurable weighted-scoring algorithm).

NOTE: this is a hand-weighted multi-criteria scoring method (a simple-additive-weighting model), NOT a
trained machine-learning model. Weights are design parameters and should be tuned/justified in the thesis.

For donation d (quantity q, urgency u, deadline T_p, usable time T_u) and each *feasible* recipient i
(distance D_i, pickup ETA P_i, delivery ETA E_i, acceptable quantity a_i = min(demand_i, capacity_i)):

  demand            s1 = demand_i / max_j demand_j                       (max over feasible set)
  quantity          s2 = min(q, a_i) / q
  distance          s3 = clip(1 - D_i / R_max)
  urgency           s4 = u * clip(1 - P_i / T_p)                         (urgent food -> fast pickup)
  usable_time       s5 = clip((T_u - E_i) / T_u)                         (slack before food expires)
  capacity          s6 = clip(capacity_i / q)
  compatibility     s7 = 1 exact category match, 0.7 wildcard ("any")
  pickup_feasib.    s8 = clip(1 - P_i / T_p)                             (slack before donor deadline)
  fairness          s9 = 0.5 * (1 - rec_i/max_j rec_j) + 0.5 * (1 - freq_i/max_j freq_j)
                         rec_i = historical_received_i / priority_i ; freq_i = allocation_count_i
                         (a term is 1 when its maximum is 0)

  score(i) = sum_k w_k * s_k / sum_k w_k       (weights are normalised to sum to 1)

Infeasible recipients (see matching_core hard constraints) are rejected before scoring.
Weights are independent: setting w_k = 0 removes factor k (used by the ablation study).
"""
from dataclasses import dataclass, asdict, fields
from typing import Dict

from app.algorithms.matching_core import MatchingOptions, allocate_donation, basic_scores, _clip

NAME = "dynamic_multi_factor"
FACTORS = ["demand", "quantity", "distance", "urgency", "usable_time", "capacity",
           "compatibility", "pickup_feasibility", "fairness"]


@dataclass
class Weights:
    demand: float = 0.15
    quantity: float = 0.10
    distance: float = 0.12
    urgency: float = 0.10
    usable_time: float = 0.10
    capacity: float = 0.08
    compatibility: float = 0.08
    pickup_feasibility: float = 0.12
    fairness: float = 0.15

    def normalized(self) -> Dict[str, float]:
        raw = asdict(self)
        if any(v < 0 for v in raw.values()):
            raise ValueError("weights must be non-negative")
        total = sum(raw.values())
        if total <= 0:
            raise ValueError("at least one weight must be positive")
        return {k: v / total for k, v in raw.items()}

    def without(self, factor: str) -> "Weights":
        if factor not in FACTORS:
            raise KeyError(factor)
        d = asdict(self)
        d[factor] = 0.0
        return Weights(**d)

    @classmethod
    def from_dict(cls, d: dict) -> "Weights":
        allowed = {f.name for f in fields(cls)}
        unknown = set(d) - allowed
        if unknown:
            raise KeyError(f"unknown weight(s): {sorted(unknown)}")
        return cls(**d)


def factor_scores(d, c, r, opts: MatchingOptions, max_demand, max_rec, max_freq, qty) -> Dict[str, float]:
    s = basic_scores(c, d, r, opts, max_demand, qty)
    u = d.urgency_value()
    timeliness = _clip(1.0 - c.pickup_eta_min / d.pickup_deadline_min) if d.pickup_deadline_min > 0 else 0.0
    slack = _clip((d.remaining_usable_min - c.delivery_eta_min) / d.remaining_usable_min) \
        if d.remaining_usable_min > 0 else 0.0
    rec = r.historical_received / max(r.priority, 1e-9)
    fair_rec = 1.0 - rec / max_rec if max_rec > 0 else 1.0
    fair_freq = 1.0 - r.allocation_count / max_freq if max_freq > 0 else 1.0
    s.update({
        "urgency": u * timeliness,
        "usable_time": slack,
        "capacity": _clip(r.capacity / qty) if qty > 0 else 0.0,
        "compatibility": r.accepts(d.category),
        "pickup_feasibility": timeliness,
        "fairness": 0.5 * _clip(fair_rec) + 0.5 * _clip(fair_freq),
    })
    return s


def make_ranker(weights: Weights = None):
    w = (weights or Weights()).normalized()

    def rank(d, feasible, recipients, opts: MatchingOptions, qty):
        max_demand = max(recipients[c.recipient_id].demand_remaining for c in feasible)
        max_rec = max(recipients[c.recipient_id].historical_received / max(recipients[c.recipient_id].priority, 1e-9)
                      for c in feasible)
        max_freq = max(recipients[c.recipient_id].allocation_count for c in feasible)
        for c in feasible:
            r = recipients[c.recipient_id]
            c.factor_scores = factor_scores(d, c, r, opts, max_demand, max_rec, max_freq, qty)
            c.weighted_contributions = {k: w[k] * c.factor_scores[k] for k in FACTORS}
            c.total_score = sum(c.weighted_contributions.values())
        return sorted(feasible, key=lambda c: (-c.total_score, c.distance_km, c.recipient_id))
    return rank


def allocate(d, recipients, opts: MatchingOptions, weights: Weights = None, explain=None, name: str = NAME):
    return allocate_donation(name, make_ranker(weights), d, recipients, opts, explain)
