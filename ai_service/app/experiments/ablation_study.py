"""Ablation study for the proposed matcher: remove one factor at a time and measure the actual change.

Variant definitions (engine-side changes; execution is always judged against the truth):
  full                : all nine factors, all hard constraints
  without_urgency     : urgency weight = 0
  without_fairness    : fairness weight = 0
  without_distance    : distance weight = 0 (hard service-radius constraint remains)
  without_usable_time : usable-time weight = 0 AND the usable-time feasibility constraint is not enforced
  without_capacity    : capacity weight = 0 AND the engine ignores recipient capacity (capacity is still
                        enforced at execution, so over-allocated food is wasted)
"""
from typing import Dict, List

from app.algorithms import dynamic_matching as dm
from app.experiments.baseline_comparison import KEY_METRICS, paired_test
from app.experiments.metrics import aggregate
from app.experiments.simulator import ScenarioConfig, generate_scenario, options_from, run_online

VARIANTS = {
    "full": ({}, {}),
    "without_urgency": ({"urgency": 0.0}, {}),
    "without_fairness": ({"fairness": 0.0}, {}),
    "without_distance": ({"distance": 0.0}, {}),
    "without_usable_time": ({"usable_time": 0.0}, {"enforce_usable_time": False}),
    "without_capacity": ({"capacity": 0.0}, {"enforce_capacity": False}),
}


def run_ablation(cfg: ScenarioConfig, seeds: List[int], base_weights: dm.Weights = None) -> Dict:
    base_weights = base_weights or dm.Weights()
    rows = {n: [] for n in VARIANTS}
    for s in seeds:
        sc = generate_scenario(cfg, s)
        for name, (wmod, omod) in VARIANTS.items():
            w = dm.Weights(**{**base_weights.__dict__, **wmod})
            opts = options_from(cfg, **omod)
            rows[name].append(run_online(sc, lambda d, r, o, w=w: dm.allocate(d, r, o, w), opts))
    summary = {n: aggregate(r) for n, r in rows.items()}
    deltas = {}
    for n in VARIANTS:
        if n == "full":
            continue
        deltas[n] = {m: {**paired_test([r[m] for r in rows["full"]], [r[m] for r in rows[n]])} for m in KEY_METRICS}
    return {"config": cfg.__dict__, "seeds": list(seeds), "summary": summary, "delta_vs_full": deltas,
            "note": "delta = variant - full (paired over identical synthetic scenarios). Positive 'potential_wastage' or "
                    "'unmet_demand' delta means the variant is WORSE; negative 'jain_fairness'/'redistributed' delta means worse."}
