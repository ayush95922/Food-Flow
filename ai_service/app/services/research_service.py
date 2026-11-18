"""Runs the research experiments for the API (bounded compute) and for the report script."""
from dataclasses import fields
from typing import Dict

from app.experiments.ablation_study import run_ablation
from app.experiments.baseline_comparison import run_comparison
from app.experiments.dynamic_timeline import run_timeline
from app.experiments.baseline_comparison import paired_test
from app.experiments.metrics import aggregate
from app.experiments.simulator import ScenarioConfig, generate_scenario


def build_config(c: dict) -> ScenarioConfig:
    allowed = {f.name for f in fields(ScenarioConfig)}
    kw = {k: v for k, v in c.items() if k in allowed and v is not None}
    for k in ("deadline_min_range", "capacity_factor_range"):
        if k in kw:
            kw[k] = tuple(kw[k])
    cfg = ScenarioConfig(**kw)
    if cfg.qty_min >= cfg.qty_max:
        raise ValueError("qty_min must be < qty_max")
    return cfg


def run_timeline_comparison(cfg: ScenarioConfig, seeds):
    rows = {"static": [], "dynamic": []}
    for s in seeds:
        sc = generate_scenario(cfg, s)
        for m in rows:
            rows[m].append(run_timeline(sc, m))
    keys = ["redistributed", "potential_wastage", "unmet_demand", "jain_fairness", "recipients_served", "avg_transport_km",
            "rejections", "rematches", "failed_delivery_qty", "matching_time_ms_per_donation"]
    return {"summary": {m: aggregate(r) for m, r in rows.items()},
            "paired_tests_dynamic_minus_static": {k: paired_test([r[k] for r in rows["static"]], [r[k] for r in rows["dynamic"]]) for k in keys},
            "per_seed": rows}


def run_research(req) -> Dict:
    try:
        cfg = build_config(req.config.model_dump())
    except (ValueError, TypeError) as e:
        from app.utils.errors import ValidationFailed
        raise ValidationFailed(str(e))
    seeds = list(range(req.base_seed, req.base_seed + req.n_seeds))
    out: Dict = {"synthetic_data_notice": "All scenarios are SYNTHETIC, generated from documented assumptions. "
                                          "Results show relative algorithm behaviour in simulation, not real-world impact.",
                 "seeds": seeds}
    if "baselines" in req.experiments:
        r = run_comparison(cfg, seeds)
        if not req.include_per_seed:
            r.pop("per_seed")
        out["baselines"] = r
    if "ablation" in req.experiments:
        out["ablation"] = run_ablation(cfg, seeds)
    if "dynamic_timeline" in req.experiments:
        r = run_timeline_comparison(cfg, seeds)
        if not req.include_per_seed:
            r.pop("per_seed")
        out["dynamic_timeline"] = r
    return out
