"""Run the research experiments (SYNTHETIC scenarios) and write reports/ (JSON, Markdown tables, PNG plots).
Usage: python scripts/run_experiments.py [--seeds 30]"""
import argparse, json, sys
from pathlib import Path
ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
from app.experiments.ablation_study import run_ablation
from app.experiments.baseline_comparison import run_comparison
from app.experiments.simulator import ScenarioConfig
from app.services.research_service import run_timeline_comparison

M = ["redistributed", "potential_wastage", "unmet_demand", "recipients_served", "avg_transport_km", "jain_fairness", "matching_time_ms_per_donation"]


def table(summary, metrics=M):
    names = list(summary)
    out = "| metric | " + " | ".join(names) + " |\n|---|" + "---|" * len(names) + "\n"
    for m in metrics:
        out += f"| {m} | " + " | ".join(f"{summary[n][m]['mean']:.2f} ± {summary[n][m]['std']:.2f}" for n in names) + " |\n"
    return out


def bar(summary, metric, path, title):
    names = list(summary)
    plt.figure(figsize=(7, 3.8))
    plt.bar(range(len(names)), [summary[n][metric]["mean"] for n in names], yerr=[summary[n][metric]["std"] for n in names], capsize=4)
    plt.xticks(range(len(names)), [n.replace("_", "\n", 1) for n in names], fontsize=7)
    plt.title(title, fontsize=10); plt.tight_layout(); plt.savefig(path, dpi=130); plt.close()


def main():
    ap = argparse.ArgumentParser(); ap.add_argument("--seeds", type=int, default=30); a = ap.parse_args()
    seeds = list(range(a.seeds))
    rep = ROOT / "reports"; rep.mkdir(exist_ok=True)
    md = ["# Research simulation results (SYNTHETIC scenarios)\n",
          f"Seeds 0..{a.seeds-1}; mean ± std over seeds. Weights are the untuned defaults in `dynamic_matching.Weights`. "
          "These numbers describe behaviour inside the simulator only.\n"]
    allr = {}
    for ratio in (0.5, 1.0, 1.5):
        cfg = ScenarioConfig(demand_supply_ratio=ratio)
        r = run_comparison(cfg, seeds); r.pop("per_seed")
        allr[f"baselines_demand_supply_{ratio}"] = r
        md.append(f"\n## Experiments A/B/C - demand/supply ratio {ratio}\n\n" + table(r["summary"]))
        md.append("\nPaired Wilcoxon tests (proposed minus baseline), p-values for redistributed / jain_fairness / avg_transport_km:\n")
        for k, v in r["paired_tests_proposed_minus_baseline"].items():
            md.append(f"- {k}: " + ", ".join(f"{m}: diff {v[m]['mean_diff']:+.2f} (p={v[m]['p_value']:.3g})" for m in ("redistributed", "jain_fairness", "avg_transport_km")))
        bar(r["summary"], "jain_fairness", rep / f"fairness_ratio_{ratio}.png", f"Jain fairness, demand/supply={ratio}")
        bar(r["summary"], "redistributed", rep / f"redistributed_ratio_{ratio}.png", f"Redistributed portions, demand/supply={ratio}")
    cfg = ScenarioConfig(demand_supply_ratio=1.0)
    ab = run_ablation(cfg, seeds); allr["ablation"] = ab
    md.append("\n## Ablation (ratio 1.0)\n\n" + table(ab["summary"]))
    md.append("\nDelta vs full (variant - full), with Wilcoxon p:\n")
    for n, d in ab["delta_vs_full"].items():
        md.append(f"- {n}: " + ", ".join(f"{m} {d[m]['mean_diff']:+.2f} (p={d[m]['p_value']:.3g})" for m in ("redistributed", "unmet_demand", "jain_fairness", "avg_transport_km")))
    bar(ab["summary"], "redistributed", rep / "ablation_redistributed.png", "Ablation: redistributed portions")
    bar(ab["summary"], "jain_fairness", rep / "ablation_fairness.png", "Ablation: Jain fairness")
    dt = run_timeline_comparison(cfg, seeds); dt.pop("per_seed"); allr["dynamic_timeline"] = dt
    keys = ["redistributed", "potential_wastage", "unmet_demand", "jain_fairness", "rejections", "rematches", "failed_delivery_qty"]
    md.append("\n## Dynamic (event-driven re-matching) vs static allocation\n\n" + table(dt["summary"], keys))
    md.append("\nPaired tests (dynamic minus static): " + "; ".join(f"{k}: {v['mean_diff']:+.2f} (p={v['p_value']:.3g})" for k, v in dt["paired_tests_dynamic_minus_static"].items() if k in keys))
    bar(dt["summary"], "redistributed", rep / "dynamic_vs_static_redistributed.png", "Dynamic vs static: redistributed portions")
    (rep / "research_results.json").write_text(json.dumps(allr, indent=2))
    (rep / "research_results.md").write_text("\n".join(md) + "\n")
    print("\n".join(md))


if __name__ == "__main__":
    main()
