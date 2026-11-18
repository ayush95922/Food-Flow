"""Train and save the usable-time regressor (SYNTHETIC data). Usage: python scripts/train_usable_time.py"""
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
from app.services.expiry_training import generate_synthetic_dataset, train_and_save  # noqa: E402

if __name__ == "__main__":
    root = Path(__file__).resolve().parent.parent
    (root / "datasets").mkdir(exist_ok=True)
    generate_synthetic_dataset().to_csv(root / "datasets" / "usable_time_SYNTHETIC.csv", index=False)
    meta = train_and_save(str(root / "saved_models" / "usable_time"))
    (root / "reports" / "usable_time_evaluation.json").write_text(json.dumps(meta, indent=2))
    print(json.dumps({k: meta[k] for k in ("selected_model", "results", "interval_halfwidth_h_q90")}, indent=2))
