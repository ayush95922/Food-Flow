import pytest

from app.experiments.ablation_study import VARIANTS, run_ablation
from app.experiments.baseline_comparison import run_comparison
from app.experiments.dynamic_timeline import run_timeline
from app.experiments.simulator import STRATEGIES, ScenarioConfig, generate_scenario, run_online

CFG = ScenarioConfig(n_donations=15, n_recipients=6)


def test_scenario_is_reproducible():
    a, b = generate_scenario(CFG, 3), generate_scenario(CFG, 3)
    assert [d.donation.quantity for d in a.donations] == [d.donation.quantity for d in b.donations]
    assert a.recipients[0].location == b.recipients[0].location
    assert [d.donation.quantity for d in generate_scenario(CFG, 4).donations] != [d.donation.quantity for d in a.donations]


@pytest.mark.parametrize("name", list(STRATEGIES))
def test_conservation_and_bounds(name):
    for seed in range(5):
        r = run_online(generate_scenario(CFG, seed), STRATEGIES[name])
        assert r["redistributed"] <= r["total_donated"] + 1e-6
        assert r["potential_wastage"] == pytest.approx(r["total_donated"] - r["redistributed"])
        assert 0 <= r["jain_fairness"] <= 1 and r["unmet_demand"] >= 0 and r["recipients_served"] <= CFG.n_recipients
        assert r["matching_time_ms_per_donation"] >= 0 and r["computational_time_s"] >= r["matching_time_total_s"]


def test_comparison_structure_and_stats():
    out = run_comparison(CFG, list(range(4)))
    assert set(out["summary"]) == set(STRATEGIES) and len(out["per_seed"]["B_rule_based"]) == 4
    t = out["paired_tests_proposed_minus_baseline"]
    assert "C_dynamic_multi_factor_vs_A_nearest_recipient" in t and "p_value" in t["C_dynamic_multi_factor_vs_A_nearest_recipient"]["redistributed"]


def test_ablation_has_all_variants_and_actual_deltas():
    out = run_ablation(CFG, list(range(4)))
    assert set(out["summary"]) == set(VARIANTS) and set(out["delta_vs_full"]) == set(VARIANTS) - {"full"}
    assert all("mean_diff" in v["redistributed"] for v in out["delta_vs_full"].values())


def test_ablation_without_capacity_wastes_food_at_execution():
    cfg = ScenarioConfig(n_donations=30, n_recipients=6, capacity_factor_range=(0.3, 0.6))
    out = run_ablation(cfg, list(range(6)))
    assert out["delta_vs_full"]["without_capacity"]["redistributed"]["mean_diff"] <= 0


@pytest.mark.parametrize("mode", ["static", "dynamic"])
def test_timeline_modes(mode):
    sc = generate_scenario(ScenarioConfig(n_donations=20, n_recipients=6), 1)
    r = run_timeline(sc, mode)
    assert r["redistributed"] <= r["total_donated"] + 1e-6 and r["potential_wastage"] >= -1e-6
    if mode == "static":
        assert r["rematches"] == 0


def test_dynamic_reacts_to_events_more_than_static():
    cfg = ScenarioConfig(n_donations=30, n_recipients=8, n_unavailable_events=8, accept_prob=0.6)
    stat = dyn = 0.0
    n = 0
    for s in range(8):
        sc = generate_scenario(cfg, s)
        stat += run_timeline(sc, "static")["redistributed"]
        d = run_timeline(sc, "dynamic")
        dyn += d["redistributed"]
        n += d["rematches"]
    assert n > 0 and dyn >= stat


def test_api_research(client):
    body = {"config": {"n_donations": 10, "n_recipients": 5}, "n_seeds": 2}
    j = client.post("/api/ai/research/run-experiment", json=body).json()
    assert {"baselines", "ablation", "dynamic_timeline"} <= set(j) and "SYNTHETIC" in j["synthetic_data_notice"]
    assert client.post("/api/ai/research/run-experiment", json={"n_seeds": 1000}).status_code == 422
    bad = client.post("/api/ai/research/run-experiment", json={"config": {"qty_min": 500, "qty_max": 100}})
    assert bad.status_code == 422
