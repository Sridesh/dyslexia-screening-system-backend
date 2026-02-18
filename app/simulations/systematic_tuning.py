import itertools
import csv
import sys
import os
from typing import Dict, Any, List

# Ensure app is in path if running directly
sys.path.append(os.getcwd())

from app.adaptive_testing_module import config
from app.simulations.sim_core import run_batch
from app.simulations.metrics import compute_metrics

PARAM_GRID = {
    "RISK_SCORE_HIGH":     [0.55, 0.60, 0.65],
    "RISK_SCORE_MODERATE": [0.40, 0.45, 0.50],
    "ENTROPY_THRESHOLD":   [0.70, 0.75, 0.80],
    "P_CONFIDENT":         [0.75, 0.80],
    "MIN_INFO_GAIN":       [0.01, 0.02, 0.03],
}

def iter_configs(grid: Dict[str, List[Any]]):
    keys = list(grid.keys())
    vals = list(grid.values())
    for combo in itertools.product(*vals):
        yield dict(zip(keys, combo))

def apply_config(cfg: Dict[str, Any]):
    for k, v in cfg.items():
        setattr(config, k, v)

def run_grid_search(num_runs_per_profile: int, seed: int = 42):
    configs = list(iter_configs(PARAM_GRID))
    best_j = -2.0 # Initialize low
    best_cfg = None
    best_metrics = None
    all_rows: List[Dict[str, Any]] = []

    # Store original config to restore later
    original = {k: getattr(config, k, None) for k in PARAM_GRID.keys()}

    print(f"Starting grid search with {len(configs)} configurations...")

    for i, cfg in enumerate(configs):
        apply_config(cfg)
        batch = run_batch(num_runs_per_profile=num_runs_per_profile, seed=seed)
        metrics = compute_metrics(batch)
        
        row = {**cfg, **metrics}
        all_rows.append(row)

        # Optimization criteria: Best Youden J, subject to short test constraint
        if metrics["youden_j"] > best_j and metrics["avg_items_all"] <= 15:
            best_j = metrics["youden_j"]
            best_cfg = cfg
            best_metrics = metrics

        log_msg = (
            f"[{i+1}/{len(configs)}] "
            f"J={metrics['youden_j']:.3f} "
            f"Sens={metrics['sensitivity']:.3f} "
            f"Spec={metrics['specificity']:.3f} "
            f"Items={metrics['avg_items_all']:.1f}\n"
        )
        print(log_msg.strip())
        with open("tuning_log.txt", "a") as f:
            f.write(log_msg)

    # Restore original config
    if original:
        apply_config(original)
        
    return all_rows, best_cfg, best_metrics

def save_results(path: str, rows: List[Dict[str, Any]]):
    if not rows:
        return
    with open(path, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=rows[0].keys())
        writer.writeheader()
        writer.writerows(rows)

if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument("--runs", type=int, default=500, help="Simulations per child profile")
    parser.add_argument("--seed", type=int, default=42, help="Random seed")
    parser.add_argument("--quick", action="store_true", help="Run a smaller grid for quick testing")
    args = parser.parse_args()

    if args.quick:
        args.runs = 20 # Small number for quick test
        # Override grid with a subset
        PARAM_GRID["RISK_SCORE_HIGH"] = [0.60, 0.65]
        PARAM_GRID["RISK_SCORE_MODERATE"] = [0.45]
        PARAM_GRID["ENTROPY_THRESHOLD"] = [0.75]
        PARAM_GRID["P_CONFIDENT"] = [0.80]
        PARAM_GRID["MIN_INFO_GAIN"] = [0.02]

    # Dynamically inject PARAM_GRID if needed, but it's global here
    
    print(f"EF-ADS tuning: runs/profile={args.runs}")
    rows, best_cfg, best_metrics = run_grid_search(args.runs, args.seed)
    save_results("tuning_grid_results.csv", rows)

    if best_cfg:
        print("\nOPTIMAL CONFIG (avg_items_all <= 15):")
        for k, v in best_cfg.items():
            print(f"  {k}: {v}")
        print(
            f"\n  Sens={best_metrics['sensitivity']:.3f}, "
            f"Spec={best_metrics['specificity']:.3f}, "
            f"J={best_metrics['youden_j']:.3f}, "
            f"Items_all={best_metrics['avg_items_all']:.1f}"
        )
    else:
        print("\nNo config met the item-length constraint; relax it or expand item bank.")
