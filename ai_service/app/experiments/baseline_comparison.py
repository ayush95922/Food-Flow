"""Experiments A / B / C: Nearest Recipient vs Rule-Based vs Proposed Dynamic Multi-Factor matching."""
from typing import Dict, List, Optional

import numpy as np
from scipy import stats

from app.experiments.metrics import aggregate
from app.experiments.simulator import STRATEGIES, ScenarioConfig, generate_scenario, run_online

KEY_METRICS = ["redistributed", "potential_wastage", "unmet_demand", "recipients_served", "avg_transport_km",
               "jain_fairness", "matching_time_ms_per_donation"]


def paired_test(a: List[float], b: List[float]) -> Dict[str, float]:
    """Paired comparison b - a over the same scenarios (Wilcoxon signed-rank; p=1 if all differences are 0)."""
    diff = np.asarray(b) - np.asarray(a)
    out = {"mean_diff": float(diff.mean()), "n": int(len(diff))}
    if np.allclose(diff, 0):
        out["p_value"] = 1.0
    else:
        try:
            out["p_value"] = float(stats.wilcoxon(diff).pvalue)
        except ValueError:
            out["p_value"] = float("nan")
    return out


def run_comparison(cfg: ScenarioConfig, seeds: List[int], strategies: Optional[Dict] = None) -> Dict:
    strategies = strategies or STRATEGIES
    per_seed: Dict[str, List[Dict]] = {n: [] for n in strategies}
    for s in seeds:
        sc = generate_scenario(cfg, s)
        for n, fn in strategies.items():
            per_seed[n].append(run_online(sc, fn))
    summary = {n: aggregate(rows) for n, rows in per_seed.items()}
    names = list(strategies)
    tests = {}
    if len(names) >= 3:
        for ref in names[:2]:
            tests[f"{names[2]}_vs_{ref}"] = {m: paired_test([r[m] for r in per_seed[ref]], [r[m] for r in per_seed[names[2]]])
                                           for m in KEY_METRICS}
    return {"config": {k: v for k, v in cfg.__dict__.items()}, "seeds": list(seeds), "summary": summary,
            "paired_tests_proposed_minus_baseline": tests, "per_seed": per_seed,
            "note": "SYNTHETIC scenarios. p-values: two-sided Wilcoxon signed-rank on per-seed paired differences, "
                    "no multiple-comparison correction."}
