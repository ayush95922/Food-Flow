"""Strategy A - Nearest Recipient baseline.

Ranks feasible recipients by (simulated road) distance only. Feasibility uses the same hard constraints
as the other strategies so that the comparison isolates the ranking rule.
    score_A = 1 - distance / max_radius      (used only to report a number; ordering = ascending distance)
"""
from app.algorithms.matching_core import MatchingOptions, allocate_donation, _clip

NAME = "nearest_recipient"


def rank(d, feasible, recipients, opts: MatchingOptions, qty):
    for c in feasible:
        c.factor_scores = {"distance": _clip(1.0 - c.distance_km / opts.max_radius_km)}
        c.weighted_contributions = dict(c.factor_scores)
        c.total_score = c.factor_scores["distance"]
    return sorted(feasible, key=lambda c: (c.distance_km, c.recipient_id))


def allocate(d, recipients, opts: MatchingOptions, explain=None):
    return allocate_donation(NAME, rank, d, recipients, opts, explain)
