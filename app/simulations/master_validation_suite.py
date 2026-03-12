import sys
import os
import random
import numpy as np
import pandas as pd
from collections import defaultdict
from dataclasses import dataclass
from typing import Dict, List, Tuple, Optional
from datetime import datetime, timedelta, timezone

# Ensure app is in path if running directly
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..")))

from app.adaptive_testing_module import config, state, bayes, selection, stopping, risk, orchestration_engine

# ==============================================================================
# 1. CORE CONFIGURATION & PROFILES
# ==============================================================================

@dataclass
class SyntheticChild:
    name: str
    theta_by_module: Dict[str, float]
    ground_truth: int # 1 if at-risk, 0 if normal
    forced_slow_ran: bool = False

PROFILES: List[SyntheticChild] = [
    SyntheticChild("Strong_All", {"phonemic_awareness": 1.5, "ran": 1.5, "object_recognition": 1.5}, ground_truth=0),
    SyntheticChild("Average_Kid", {"phonemic_awareness": 0.0, "ran": 0.0, "object_recognition": 0.0}, ground_truth=0),
    SyntheticChild("Borderline_All", {"phonemic_awareness": -0.3, "ran": -0.3, "object_recognition": -0.3}, ground_truth=0),
    SyntheticChild("PA_only_mild", {"phonemic_awareness": -0.8, "ran": 0.0, "object_recognition": 0.0}, ground_truth=1),
    SyntheticChild("PA_only_severe", {"phonemic_awareness": -1.5, "ran": 0.0, "object_recognition": 0.0}, ground_truth=1),
    SyntheticChild("RAN_only_mild", {"phonemic_awareness": 0.0, "ran": -0.8, "object_recognition": 0.0}, ground_truth=1),
    SyntheticChild("RAN_only_severe", {"phonemic_awareness": 0.0, "ran": -1.5, "object_recognition": 0.0}, ground_truth=1),
    SyntheticChild("Double_deficit_mild", {"phonemic_awareness": -0.8, "ran": -0.8, "object_recognition": 0.0}, ground_truth=1),
    SyntheticChild("Double_deficit_severe", {"phonemic_awareness": -1.5, "ran": -1.5, "object_recognition": 0.0}, ground_truth=1),
    SyntheticChild("Visual_primary", {"phonemic_awareness": 0.0, "ran": 0.0, "object_recognition": -1.2}, ground_truth=0),
    SyntheticChild("Slow_But_Accurate_RAN", {"phonemic_awareness": 0.0, "ran": 0.0, "object_recognition": 0.0}, ground_truth=1, forced_slow_ran=True),
]

# ==============================================================================
# 2. ITEM BANK & RESPONSE ENGINE
# ==============================================================================

def make_synthetic_item_bank() -> Tuple[Dict[int, selection.CandidateItem], Dict[str, List[int]]]:
    """Generates a large synthetic bank for robust simulation."""
    items = {}
    item_id = 1
    difficulties = np.linspace(-3.0, 3.0, 50)
    
    for module_id in config.MODULES: 
        for b in difficulties:
            items[item_id] = selection.CandidateItem(
                id=item_id,
                module_id=module_id,
                difficulty=float(b),
                max_time_seconds=random.uniform(3.0, 7.0),
            )
            item_id += 1

    module_item_ids = {}
    for item in items.values():
        module_item_ids.setdefault(item.module_id, []).append(item.id)

    return items, module_item_ids

def simulate_response(child: SyntheticChild, item: selection.CandidateItem) -> Tuple[bool, float]:
    """Simulates a 4PL-based response with fatigue and RT variance."""
    theta = child.theta_by_module.get(item.module_id, 0.0)
    a = config.ITEM_DISCRIMINATION.get(item.module_id, 1.0)
    c = config.ITEM_GUESSING.get(item.module_id, 0.0)
    d = config.ITEM_SLIPPING.get(item.module_id, 0.0)
    b = item.difficulty

    # 4PL Probability
    p_correct = bayes.prob_correct(theta, a, b, c, d)
    is_correct = random.random() < p_correct

    # RT Model
    base_rt = item.max_time_seconds * 0.5
    diff_effect = max(0, b - theta) * 1.5 
    noise = random.uniform(-1.0, 1.0)
    rt_seconds = max(1.0, base_rt + diff_effect + noise)
    
    if child.forced_slow_ran and item.module_id == "ran":
        rt_seconds += 6.0 
        
    rt_seconds = min(rt_seconds, item.max_time_seconds + 5.0) 
    return is_correct, rt_seconds

# ==============================================================================
# 3. SIMULATION EXECUTION
# ==============================================================================

def run_single_simulation(child: SyntheticChild, test_id: int, item_pool, module_item_ids) -> Dict:
    """Simulates a full adaptive screening session for one child."""
    start_time = datetime.now(timezone.utc)
    res = orchestration_engine.start_new_test(test_id, module_item_ids, item_pool, start_time)

    session = res.session
    current_item = res.first_item
    global_risk = None
    steps = 0
    
    while current_item is not None and steps < 150:
        steps += 1
        is_correct, rt_seconds = simulate_response(child, current_item)
        sim_time = start_time + timedelta(seconds=(steps * 5))

        step_res = orchestration_engine.process_response(
            session=session,
            module_id=current_item.module_id,
            item=current_item,
            is_correct=is_correct,
            rt_seconds=rt_seconds,
            response_timestamp=sim_time,
            item_pool=item_pool,
        )

        session = step_res.session
        if step_res.should_stop:
            global_risk = step_res.global_risk
            break
        current_item = step_res.next_item

    if not global_risk:
        global_risk = risk.compute_global_risk(session)

    # Final stats
    est_thetas = {}
    for mid, m in session.modules.items():
        est_thetas[mid] = sum(p * t for p, t in zip(m.theta_posterior, config.THETA_GRID))

    return {
        "profile": child.name,
        "ground_truth": child.ground_truth,
        "risk_category": global_risk.risk_category if global_risk else "low",
        "risk_score": global_risk.risk_score if global_risk else 0.0,
        "subtype": global_risk.subtype if global_risk else "None",
        "total_items": sum(m.num_items for m in session.modules.values()),
        "total_time": session.total_time_seconds,
        "est_thetas": est_thetas
    }

# ==============================================================================
# 4. REPORTING & METRICS
# ==============================================================================

def generate_report(results: List[Dict]):
    df = pd.DataFrame(results)
    
    # 1. Profile Breakdown Table
    print("\n" + "="*100)
    print(f"{'PROFILE NAME':<25} | {'RISK (H/M/L) %':<20} | {'TOP SUBTYPE':<20} | {'AVG ITEMS'}")
    print("-" * 100)
    
    for profile_name in [p.name for p in PROFILES]:
        p_df = df[df['profile'] == profile_name]
        n = len(p_df)
        if n == 0: continue
        
        counts = p_df['risk_category'].value_counts(normalize=True).to_dict()
        h_pct = counts.get('high', 0) * 100
        m_pct = counts.get('moderate', 0) * 100
        l_pct = counts.get('low', 0) * 100
        
        top_subtype = p_df['subtype'].mode()[0]
        avg_items = p_df['total_items'].mean()
        
        risk_str = f"{h_pct:0.0f}/{m_pct:0.0f}/{l_pct:0.0f}"
        print(f"{profile_name:<25} | {risk_str:<20} | {top_subtype:<20} | {avg_items:.1f}")

    # 2. Global Clinicial Metrics
    # Treat 'high' and 'moderate' as Predicted Positive
    df['predicted_positive'] = df['risk_category'].isin(['high', 'moderate'])
    
    tp = len(df[(df['ground_truth'] == 1) & (df['predicted_positive'] == True)])
    fn = len(df[(df['ground_truth'] == 1) & (df['predicted_positive'] == False)])
    tn = len(df[(df['ground_truth'] == 0) & (df['predicted_positive'] == False)])
    fp = len(df[(df['ground_truth'] == 0) & (df['predicted_positive'] == True)])
    
    sensitivity = tp / (tp + fn) if (tp + fn) > 0 else 0
    specificity = tn / (tn + fp) if (tn + fp) > 0 else 0
    
    print("-" * 100)
    print(f"OVERALL SENSITIVITY: {sensitivity:.2%}  |  OVERALL SPECIFICITY: {specificity:.2%}")
    
    # 3. AUC Calculation
    try:
        from sklearn.metrics import roc_auc_score
        auc = roc_auc_score(df['ground_truth'], df['risk_score'])
        print(f"AREA UNDER CURVE (AUC): {auc:.4f}")
    except ImportError:
        print("AUC: sklearn not installed")
    
    print("="*100 + "\n")

    # 4. Performance Assessment (The "Brutal Honesty" Section)
    print("CLINICAL ASSESSMENT SUMMARY:")
    if sensitivity > 0.85 and specificity > 0.80:
        print(">> Status: EXCELLENT. The tool meets high clinical screening standards.")
    elif sensitivity > 0.75 and specificity > 0.70:
        print(">> Status: GOOD. Reliable for preliminary screening but has some noise.")
    else:
        print(">> Status: CAUTION. Model requires further threshold tuning or higher item caps.")
    print("-" * 100 + "\n")

# ==============================================================================
# 5. MAIN ENTRY POINT
# ==============================================================================

def main():
    print(f"\nEF-ADS MASTER VALIDATION SUITE v1.0")
    print(f"Engine Configuration: ML_MODEL_TYPE = {getattr(config, 'ML_MODEL_TYPE', 'logistic_regression')}")
    print(f"Running 50 simulations per profile (550 tests total)...")
    
    item_pool, module_item_ids = make_synthetic_item_bank()
    results = []
    
    random.seed(42)
    np.random.seed(42)

    for child in PROFILES:
        print(f"Simulating {child.name}...", end=" ", flush=True)
        for i in range(50):
            results.append(run_single_simulation(child, i, item_pool, module_item_ids))
        print("Done.")

    generate_report(results)

if __name__ == "__main__":
    main()
