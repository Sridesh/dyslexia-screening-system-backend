import os

files_to_delete = [
    "app/simulations/check_rf.py",
    "app/simulations/dump_rf_roc.py",
    "app/simulations/generate_ml_dataset.py",
    "app/simulations/item_bank.py",
    "app/simulations/metrics.py",
    "app/simulations/profile_breakdown.py",
    "app/simulations/profiles.py",
    "app/simulations/sim_core.py",
    "app/simulations/simulate_ef_ads.py",
    "app/simulations/systematic_tuning.py",
    "app/simulations/test_random_forest.py",
    "app/simulations/train_rf_model.py",
    "app/simulations/tune_rf_thresholds.py"
]

for f in files_to_delete:
    if os.path.exists(f):
        try:
            os.remove(f)
            print(f"Deleted: {f}")
        except Exception as e:
            print(f"Error deleting {f}: {e}")
    else:
        print(f"File not found: {f}")
