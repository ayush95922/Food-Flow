import pytest

from app.algorithms import dynamic_matching as dm, nearest_recipient as nr, rule_based as rb
from app.algorithms.explain import build_explanation
from app.algorithms.matching_core import MatchingOptions, evaluate_candidates
from app.algorithms.models import Donation, Recipient

D = Donation("D1", "cooked_meal", 100, (22.72, 75.86), 120, 240)


def recs():
    return [Recipient("A", "A", (22.73, 75.87), 80, 100, ["cooked_meal"], historical_received=500, allocation_count=5),
            Recipient("B", "B", (22.78, 75.90), 150, 200, ["any"], historical_received=20, allocation_count=1),
            Recipient("C", "C", (22.72, 75.86), 0, 50, ["any"])]


@pytest.mark.parametrize("mod", [nr, rb, dm])
def test_never_allocates_more_than_available_or_acceptable(mod):
    res = mod.allocate(D, recs(), MatchingOptions())
    assert sum(a.quantity for a in res.allocations) <= D.quantity + 1e-9
    cap = {"A": 80, "B": 150}
    per = {}
    for a in res.allocations:
        per[a.recipient_id] = per.get(a.recipient_id, 0) + a.quantity
    assert all(per[k] <= cap[k] + 1e-9 for k in per)
    assert "C" not in per                       # no remaining demand -> infeasible


def test_hard_constraints_reject_infeasible():
    o = MatchingOptions()
    rs = [Recipient("U", "U", (22.72, 75.86), 50, 50, available=False),
          Recipient("X", "X", (22.72, 75.86), 50, 50, ["bakery_dry"]),
          Recipient("F", "F", (23.5, 76.5), 50, 50),                       # far away
          Recipient("W", "W", (22.72, 75.86), 50, 50, available_in_min=500),  # cannot pick up before deadline
          Recipient("OK", "OK", (22.72, 75.86), 50, 50)]
    codes = {c.recipient_id: c.rejection_reasons for c in evaluate_candidates(D, rs, o)}
    assert "recipient_unavailable" in codes["U"] and "category_not_accepted" in codes["X"]
    assert "outside_service_radius" in codes["F"] and "pickup_deadline_missed" in codes["W"] and codes["OK"] == []


def test_usable_time_constraint_and_ablation_switch():
    short = Donation("S", "cooked_meal", 10, (22.72, 75.86), 120, 20)
    far = [Recipient("R", "R", (22.76, 75.90), 50, 50)]                    # ~7 km road -> delivery ~40 min > 20 min
    assert "usable_time_exceeded" in evaluate_candidates(short, far, MatchingOptions())[0].rejection_reasons
    assert evaluate_candidates(short, far, MatchingOptions(enforce_usable_time=False))[0].feasible


def test_nearest_prefers_closest():
    res = nr.allocate(D, [Recipient("N", "N", (22.721, 75.861), 100, 100), Recipient("F", "F", (22.75, 75.9), 100, 100)], MatchingOptions())
    assert res.allocations[0].recipient_id == "N"


def test_dynamic_uses_fairness_and_demand():
    res = dm.allocate(D, recs(), MatchingOptions(), explain=build_explanation)
    assert res.allocations[0].recipient_id == "B"                          # low history, high demand, takes all 100
    assert res.allocations[0].quantity == 100


def test_factor_scores_normalised_and_weights_sum_to_one():
    res = dm.allocate(D, recs(), MatchingOptions())
    for c in res.candidates:
        if c.feasible:
            assert set(c.factor_scores) == set(dm.FACTORS) and all(0 <= v <= 1 for v in c.factor_scores.values())
    assert sum(dm.Weights().normalized().values()) == pytest.approx(1.0)
    assert sum(dm.Weights(demand=5, fairness=5).normalized().values()) == pytest.approx(1.0)


def test_weights_are_independent_and_validated():
    w = dm.Weights().without("fairness").normalized()
    assert w["fairness"] == 0
    with pytest.raises(ValueError):
        dm.Weights(demand=-1).normalized()
    with pytest.raises(KeyError):
        dm.Weights.from_dict({"bogus": 1})


def test_weights_change_ranking():
    only_dist = dm.Weights(demand=0, quantity=0, distance=1, urgency=0, usable_time=0, capacity=0, compatibility=0, pickup_feasibility=0, fairness=0)
    near = Recipient("N", "N", (22.721, 75.861), 100, 100, historical_received=9999, allocation_count=50)
    far = Recipient("F", "F", (22.75, 75.9), 100, 100)
    assert dm.allocate(D, [near, far], MatchingOptions(), only_dist).allocations[0].recipient_id == "N"
    only_fair = dm.Weights(demand=0, quantity=0, distance=0, urgency=0, usable_time=0, capacity=0, compatibility=0, pickup_feasibility=0, fairness=1)
    assert dm.allocate(D, [near, far], MatchingOptions(), only_fair).allocations[0].recipient_id == "F"


def test_explanation_is_grounded_in_scores():
    res = dm.allocate(D, recs(), MatchingOptions(), explain=build_explanation)
    ex = res.allocations[0].explanation
    strong = {k for k, v in ex["factor_scores"].items() if v >= 0.7}
    assert len(ex["reasons"]) == len(strong) or "No single factor" in ex["reasons"][0]
    assert ex["runner_up"]["recipient"] == "A"


def test_recalculation_after_state_change():
    rs = recs()
    first = dm.allocate(D, rs, MatchingOptions()).allocations[0].recipient_id
    rs[1].available = False                      # recipient B becomes unavailable -> recommendation must change
    second = dm.allocate(D, rs, MatchingOptions()).allocations[0].recipient_id
    assert first == "B" and second == "A"


def test_split_allocation_when_no_single_recipient_fits():
    rs = [Recipient("A", "A", (22.72, 75.86), 60, 60), Recipient("B", "B", (22.73, 75.87), 60, 60)]
    res = dm.allocate(D, rs, MatchingOptions())
    assert sum(a.quantity for a in res.allocations) == pytest.approx(100) and len(res.allocations) == 2


def test_unallocated_when_nothing_feasible():
    res = dm.allocate(D, [Recipient("X", "X", (22.72, 75.86), 0, 10)], MatchingOptions())
    assert res.allocations == [] and res.unallocated_qty == 100


def test_derived_urgency_range():
    assert 0 <= Donation("a", "x", 1, (0, 0), 10, 30).urgency_value() <= 1
    assert Donation("a", "x", 1, (0, 0), 10, 30).urgency_value() > Donation("a", "x", 1, (0, 0), 10, 300).urgency_value()


# --------------------------------------------------------------------- API
PAYLOAD = {
    "donations": [{"id": "D1", "food_category": "cooked_meal", "quantity": 100, "location": {"lat": 22.72, "lon": 75.86},
                   "pickup_deadline_minutes": 120, "remaining_usable_minutes": 240}],
    "recipients": [{"id": "A", "name": "NGO A", "location": {"lat": 22.73, "lon": 75.87}, "demand_remaining": 80, "capacity": 100,
                    "accepted_categories": ["cooked_meal"], "historical_received": 500, "allocation_count": 5},
                   {"id": "B", "name": "NGO B", "location": {"lat": 22.78, "lon": 75.90}, "demand_remaining": 150, "capacity": 200,
                    "historical_received": 20, "allocation_count": 1}]}


def test_api_recommend(client):
    r = client.post("/api/ai/matching/recommend", json=PAYLOAD)
    assert r.status_code == 200
    j = r.json()
    assert j["results"][0]["allocations"][0]["recipient_id"] == "B"
    assert j["results"][0]["allocations"][0]["explanation"]["reasons"]
    assert abs(sum(j["weights_used"].values()) - 1) < 1e-9
    assert j["updated_recipient_states"][1]["demand_remaining"] == 50


def test_api_compare_and_strategies(client):
    r = client.post("/api/ai/matching/recommend", json={**PAYLOAD, "compare_strategies": True, "strategy": "nearest"})
    j = r.json()
    assert r.status_code == 200 and set(j["comparison"]) == {"nearest", "rule_based", "dynamic"}


def test_api_validation_errors(client):
    bad = {**PAYLOAD, "donations": [{**PAYLOAD["donations"][0], "quantity": -5}]}
    assert client.post("/api/ai/matching/recommend", json=bad).status_code == 422
    dup = {**PAYLOAD, "recipients": [PAYLOAD["recipients"][0], PAYLOAD["recipients"][0]]}
    assert client.post("/api/ai/matching/recommend", json=dup).status_code == 422
    badw = {**PAYLOAD, "weights": {"demand": -1}}
    assert client.post("/api/ai/matching/recommend", json=badw).status_code == 422
    assert client.post("/api/ai/matching/recommend", json={}).json()["error"]["code"] == "VALIDATION_ERROR"


def test_api_batch_state_carries_over(client):
    p = {**PAYLOAD, "donations": [PAYLOAD["donations"][0], {**PAYLOAD["donations"][0], "id": "D2"}]}
    j = client.post("/api/ai/matching/recommend", json=p).json()
    total = sum(a["quantity"] for r in j["results"] for a in r["allocations"])
    assert total <= 200 and j["summary"]["allocated_quantity"] == pytest.approx(total)
    assert all(s["demand_remaining"] >= 0 for s in j["updated_recipient_states"])
