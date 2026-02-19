# app/simulations/profile_breakdown.py
import sys
import os
from collections import defaultdict

sys.path.append(os.getcwd())

from app.adaptive_testing_module import config
from app.simulations.sim_core import run_batch
from app.simulations.profiles import PROFILES  # SyntheticChild list

# Paste your tuned best config here
BEST_CFG = {
    "RISK_SCORE_HIGH": 0.55,
    "RISK_SCORE_MODERATE": 0.40,
    "ENTROPY_THRESHOLD": 0.70,
    "P_CONFIDENT": 0.75,
    "MIN_INFO_GAIN": 0.01,
}


def apply_best_config():
    for k, v in BEST_CFG.items():
        setattr(config, k, v)


def profile_breakdown(num_runs_per_profile: int = 500, seed: int = 123):
    apply_best_config()
    results = run_batch(num_runs_per_profile=num_runs_per_profile, seed=seed)

    # Global counters for at-risk vs not-at-risk misclassification
    at_risk_TP = at_risk_FN = 0
    safe_TN = safe_FP = 0

    for child in PROFILES:
        name = child.name
        data = results[name]
        gt = data["ground_truth"]

        cats = defaultdict(int)
        items = []

        for r in data["runs"]:
            cat = r["risk_category"]
            cats[cat] += 1
            items.append(r["total_items"])

            predicted_positive = cat in ("high", "moderate")
            if gt == "at_risk":
                if predicted_positive:
                    at_risk_TP += 1
                else:
                    at_risk_FN += 1
            else:
                if predicted_positive:
                    safe_FP += 1
                else:
                    safe_TN += 1

        n = len(data["runs"])
        avg_items = sum(items) / n if n > 0 else 0.0

        print(f"\n{name} (GT={gt}):")
        print(f"  Avg items: {avg_items:.1f}")
        for cat in ("high", "moderate", "low"):
            count = cats[cat]
            pct = count / n if n > 0 else 0.0
            print(f"  {cat}: {count} ({pct:.1%})")

    # Global sensitivity / specificity check for sanity
    sens = at_risk_TP / (at_risk_TP + at_risk_FN) if (at_risk_TP + at_risk_FN) > 0 else 0.0
    spec = safe_TN / (safe_TN + safe_FP) if (safe_TN + safe_FP) > 0 else 0.0

    print("\n--- Global check from profile breakdown runs ---")
    print(f"  Sensitivity: {sens:.3f}")
    print(f"  Specificity: {spec:.3f}")


if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser()
    parser.add_argument("--runs", type=int, default=500, help="Simulations per profile")
    parser.add_argument("--seed", type=int, default=123, help="Random seed")
    args = parser.parse_args()

    profile_breakdown(num_runs_per_profile=args.runs, seed=args.seed)
