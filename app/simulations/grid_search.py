import sys
import os
import random
import numpy as np
import pandas as pd

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..")))

from app.adaptive_testing_module import config
from app.simulations.master_validation_suite import PROFILES, make_synthetic_item_bank, run_single_simulation

def main():
    print("Generating single deterministic validation suite (550 runs)...")
    config.ML_MODEL_TYPE = "random_forest"
    
    random.seed(42)
    np.random.seed(42)
    
    item_pool, module_item_ids = make_synthetic_item_bank()
    results = []
    
    for child in PROFILES:
        for i in range(50):
            results.append(run_single_simulation(child, i, item_pool, module_item_ids))
            
    df = pd.DataFrame(results)
    
    print("\nSweeping RISK_SCORE_MODERATE from 0.20 to 0.60...")
    print(f"{'Threshold':<12} | {'Sensitivity %':<15} | {'Specificity %':<15} | {'Sum'}")
    print("-" * 60)
    
    best_sum = 0
    best_thresh = 0
    best_sens = 0
    best_spec = 0
    
    for t_int in range(20, 61):
        t = t_int / 100.0
        
        # Apply threshold to the SAME dataset
        df['predicted_positive'] = df['risk_score'] >= t
        
        tp = len(df[(df['ground_truth'] == 1) & (df['predicted_positive'] == True)])
        fn = len(df[(df['ground_truth'] == 1) & (df['predicted_positive'] == False)])
        tn = len(df[(df['ground_truth'] == 0) & (df['predicted_positive'] == False)])
        fp = len(df[(df['ground_truth'] == 0) & (df['predicted_positive'] == True)])
        
        sens = (tp / (tp + fn)) * 100 if (tp + fn) > 0 else 0
        spec = (tn / (tn + fp)) * 100 if (tn + fp) > 0 else 0
        
        bal_sum = sens + spec
        
        if bal_sum > best_sum:
            best_sum = bal_sum
            best_thresh = t
            best_sens = sens
            best_spec = spec
            
        if t_int % 5 == 0:
            print(f"{t:<12.2f} | {sens:<15.2f} | {spec:<15.2f} | {bal_sum:.2f}")

    print("-" * 60)
    print(f"ABSOLUTE OPTIMAL THRESHOLD: {best_thresh:.2f}")
    print(f"Optimal Sensitivity: {best_sens:.2f}%")
    print(f"Optimal Specificity: {best_spec:.2f}%")

if __name__ == "__main__":
    main()
