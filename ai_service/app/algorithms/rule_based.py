"""Strategy B - Rule-based matching (distance, demand, quantity).

    score_B = 0.40 * distance_score + 0.35 * demand_score + 0.25 * quantity_score
    distance_score = 1 - d/R_max          demand_score = demand_i / max_j demand_j  (over feasible set)
    quantity_score = min(q, acceptable_i) / q
The coefficients are fixed, hand-chosen rules (not learned).
"""
from app.algorithms.matching_core import MatchingOptions, allocate_donation, basic_scores

NAME = "rule_based"
RULE_WEIGHTS = {"distance": 0.40, "demand": 0.35, "quantity": 0.25}


def rank(d, feasible, recipients, opts: MatchingOptions, qty):
    max_demand = max(recipients[c.recipient_id].demand_remaining for c in feasible)
    for c in feasible:
        r = recipients[c.recipient_id]
        s = basic_scores(c, d, r, opts, max_demand, qty)
        c.factor_scores = {k: s[k] for k in RULE_WEIGHTS}
        c.weighted_contributions = {k: RULE_WEIGHTS[k] * s[k] for k in RULE_WEIGHTS}
        c.total_score = sum(c.weighted_contributions.values())
    return sorted(feasible, key=lambda c: (-c.total_score, c.distance_km, c.recipient_id))


def allocate(d, recipients, opts: MatchingOptions, explain=None):
    return allocate_donation(NAME, rank, d, recipients, opts, explain)
