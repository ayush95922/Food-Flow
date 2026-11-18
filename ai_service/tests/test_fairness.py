import numpy as np
import pytest

from app.algorithms.fairness_optimizer import (FairRecipient as R, allocate_fairly, fcfs_allocation, gini, jain_index,
                                                max_min_allocation, proportional_allocation)


def test_jain_known_values():
    assert jain_index([5, 5, 5, 5]) == pytest.approx(1.0)
    assert jain_index([10, 0, 0, 0]) == pytest.approx(0.25)
    assert jain_index([]) == 1.0 and jain_index([0, 0]) == 1.0
    assert 0.25 <= jain_index([1, 2, 3, 4]) <= 1.0


def test_gini_extremes():
    assert gini([5, 5, 5]) == pytest.approx(0.0)
    assert gini([0, 0, 10]) > 0.6


def rs():
    return [R("A", "A", 100, 100, 500, 10), R("B", "B", 100, 100, 0, 0), R("C", "C", 100, 100, 100, 2, 2.0)]


def test_allocation_respects_supply_and_caps():
    for supply in (0, 10, 150, 299, 300, 1000):
        x = max_min_allocation(supply, rs())["x"]
        assert x.sum() <= min(supply, 300) + 1e-6 and (x <= 100 + 1e-9).all() and (x >= -1e-12).all()
        assert x.sum() == pytest.approx(min(supply, 300), abs=1e-4)


def test_least_served_recipient_gets_priority():
    x = max_min_allocation(100, rs())["x"]
    assert x[1] > x[2] > x[0] and x[0] == pytest.approx(0, abs=1e-6)


def test_capacity_cap_binding():
    x = max_min_allocation(100, [R("A", "A", 100, 10), R("B", "B", 100, 100)])["x"]
    assert x[0] == pytest.approx(10) and x[1] == pytest.approx(90)


def test_equalises_cumulative_received_per_priority():
    out = max_min_allocation(150, [R("A", "A", 200, 200, 0, 0), R("B", "B", 200, 200, 0, 0, 2.0)])["x"]
    assert out[1] == pytest.approx(2 * out[0], rel=1e-3)               # priority 2 gets double


def test_fair_beats_ordinary_on_cumulative_fairness():
    out = allocate_fairly(150, rs())
    f = out["metrics"]["jain_cumulative_per_priority"]
    assert f >= out["comparison"]["proportional"]["metrics"]["jain_cumulative_per_priority"] - 1e-9
    assert f >= out["comparison"]["fcfs"]["metrics"]["jain_cumulative_per_priority"] - 1e-9
    assert out["metrics"]["unmet_demand_total"] == pytest.approx(300 - 150)
    assert out["explanations"][1]["reasons"]


def test_baselines_sane():
    r = rs()
    assert proportional_allocation(150, r).sum() == pytest.approx(150)
    assert fcfs_allocation(150, r)[0] == 100
    assert proportional_allocation(0, r).sum() == 0


def test_api(client):
    body = {"supply": 150, "recipients": [{"id": "A", "name": "A", "demand": 100, "capacity": 100, "historical_received": 500, "allocation_count": 10},
                                         {"id": "B", "name": "B", "demand": 100, "capacity": 100}]}
    j = client.post("/api/ai/allocation/fairness", json=body).json()
    assert sum(a["allocated"] for a in j["allocations"]) == pytest.approx(150, abs=1e-3)
    assert client.post("/api/ai/allocation/fairness", json={**body, "supply": -1}).status_code == 422
