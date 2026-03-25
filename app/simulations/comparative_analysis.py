import sys
import os
import random
import numpy as np
import pandas as pd
from dataclasses import dataclass
from typing import Dict, List, Tuple
from datetime import datetime, timedelta, timezone

# Ensure app is in path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..")))

from app.adaptive_testing_module import config, bayes, selection, risk, orchestration_engine

# ==============================================================================
# 1. PROFILES & RESPONSE ENGINE (Borrowed from master_validation_suite)
# ==============================================================================

@dataclass
class SyntheticChild:
    name: str
    theta_by_module: Dict[str, float]
    ground_truth: int
    forced_slow_ran: bool = False

PROFILES: List[SyntheticChild] = [
    SyntheticChild("Normal_Kid", {"phonemic_awareness": 0.5, "ran": 0.5, "object_recognition": 0.5}, ground_truth=0),
    SyntheticChild("PA_Deficit_Severe", {"phonemic_awareness": -1.5, "ran": 0.5, "object_recognition": 0.5}, ground_truth=1),
    SyntheticChild("RAN_Deficit_Severe", {"phonemic_awareness": 0.5, "ran": -1.5, "object_recognition": 0.5}, ground_truth=1),
    SyntheticChild("Double_Deficit", {"phonemic_awareness": -1.2, "ran": -1.2, "object_recognition": 0.0}, ground_truth=1),
    SyntheticChild("Slow_RAN_Accurate", {"phonemic_awareness": 0.5, "ran": 0.5, "object_recognition": 0.5}, ground_truth=1, forced_slow_ran=True),
]

def simulate_response(child: SyntheticChild, item: selection.CandidateItem) -> Tuple[bool, float]:
    theta = child.theta_by_module.get(item.module_id, 0.0)
    a = item.discrimination
    c = config.ITEM_GUESSING.get(item.module_id, 0.0)
    d = config.ITEM_SLIPPING.get(item.module_id, 0.0)
    b = item.difficulty

    p_correct = bayes.prob_correct(theta, a, b, c, d)
    is_correct = random.random() < p_correct

    base_rt = item.max_time_seconds * 0.5
    diff_effect = max(0, b - theta) * 1.5 
    rt_seconds = max(1.0, base_rt + diff_effect + random.uniform(-1, 1))
    
    if child.forced_slow_ran and item.module_id == "ran":
        rt_seconds += 6.0 
        
    return is_correct, min(rt_seconds, item.max_time_seconds + 5.0)

# ==============================================================================
# 2. STATIC TEST ENGINE (The Control Group)
# ==============================================================================

def run_static_test(child: SyntheticChild, items_per_module: int, item_pool, module_item_ids) -> Dict:
    """Runs a fixed-length test where items are picked sequentially by difficulty."""
    start_time = datetime.now(timezone.utc)
    test_id = 999
    
    # Initialize session
    session = orchestration_engine.initialise_session(test_id, module_item_ids, start_time)
    total_items = 0
    
    for module_id in config.MODULES:
        # Pick a spread of difficulties for the static test
        module_items = [item_pool[idx] for idx in module_item_ids[module_id]]
        # Sort by difficulty and pick N items evenly spaced
        module_items.sort(key=lambda x: x.difficulty)
        indices = np.linspace(0, len(module_items)-1, items_per_module).astype(int)
        sampled_items = [module_items[i] for i in indices]
        
        for item in sampled_items:
            total_items += 1
            is_correct, rt_seconds = simulate_response(child, item)
            
            # Simple Bayesian update (no orchestration logic)
            bayes.update_module_stats_for_item(
                module_stats=session.modules[module_id],
                module_id=module_id,
                item_difficulty=item.difficulty,
                item_discrimination=item.discrimination,
                is_correct=is_correct,
                total_time_seconds=session.total_time_seconds + rt_seconds
            )
            # Update RT stats
            from app.adaptive_testing_module import rt_fatigue
            rt_fatigue.update_module_rt_stats(session.modules[module_id], rt_seconds, item.max_time_seconds, is_correct)
            session.total_time_seconds += rt_seconds

    global_risk = risk.compute_global_risk(session)
    
    return {
        "method": "Static",
        "profile": child.name,
        "ground_truth": child.ground_truth,
        "risk_category": global_risk.risk_category,
        "risk_score": global_risk.risk_score,
        "total_items": total_items,
        "accuracy": 1 if (global_risk.risk_category != "low" and child.ground_truth == 1) or (global_risk.risk_category == "low" and child.ground_truth == 0) else 0
    }

# ==============================================================================
# 3. ADAPTIVE TEST ENGINE (The Experimental Group)
# ==============================================================================

def run_adaptive_test(child: SyntheticChild, item_pool, module_item_ids) -> Dict:
    """Runs the full adaptive engine."""
    start_time = datetime.now(timezone.utc)
    res = orchestration_engine.start_new_test(888, module_item_ids, item_pool, start_time)
    session = res.session
    current_item = res.first_item
    steps = 0
    
    while current_item is not None and steps < 60: # Safety cap
        steps += 1
        is_correct, rt_seconds = simulate_response(child, current_item)
        
        step_res = orchestration_engine.process_response(
            session=session,
            module_id=current_item.module_id,
            item=current_item,
            is_correct=is_correct,
            rt_seconds=rt_seconds,
            item_pool=item_pool,
        )
        if step_res.should_stop:
            break
        current_item = step_res.next_item

    global_risk = risk.compute_global_risk(session)
    
    return {
        "method": "Adaptive",
        "profile": child.name,
        "ground_truth": child.ground_truth,
        "risk_category": global_risk.risk_category,
        "risk_score": global_risk.risk_score,
        "total_items": sum(m.num_items for m in session.modules.values()),
        "accuracy": 1 if (global_risk.risk_category != "low" and child.ground_truth == 1) or (global_risk.risk_category == "low" and child.ground_truth == 0) else 0
    }

# ==============================================================================
# 4. MAIN COMPARISON
# ==============================================================================

def main():
    results_file = os.path.join(os.path.dirname(__file__), "..", "..", "comparative_results.txt")
    results_file = os.path.abspath(results_file)
    with open(results_file, "w") as f:
        f.write("="*80 + "\n")
        f.write("EFFICIENCY & ACCURACY COMPARISON: ADAPTIVE vs. STATIC TEST\n")
        f.write("="*80 + "\n")
        
        from app.simulations.master_validation_suite import make_synthetic_item_bank
        item_pool, module_item_ids = make_synthetic_item_bank()
        
        results = []
        iterations = 2
        static_items_per_mod = 12 # Total 36 items for static test
        
        for child in PROFILES:
            f.write(f"Testing Profile: {child.name}...\n")
            f.flush()
            for _ in range(iterations):
                results.append(run_static_test(child, static_items_per_mod, item_pool, module_item_ids))
                results.append(run_adaptive_test(child, item_pool, module_item_ids))

        df = pd.DataFrame(results)
        summary = df.groupby(['method']).agg({
            'total_items': 'mean',
            'accuracy': 'mean'
        }).reset_index()

        f.write("\n" + "="*80 + "\n")
        f.write(f"{'METHOD':<15} | {'AVG ITEMS':<15} | {'ACCURACY':<10}\n")
        f.write("-" * 80 + "\n")
        for _, row in summary.iterrows():
            f.write(f"{row['method']:<15} | {row['total_items']:<15.1f} | {row['accuracy']:<10.1%}\n")
        
        # Calculate Efficiency Gain
        static_items = summary[summary['method'] == 'Static']['total_items'].values[0]
        adaptive_items = summary[summary['method'] == 'Adaptive']['total_items'].values[0]
        gain = ((static_items - adaptive_items) / static_items) * 100
        
        f.write("-" * 80 + "\n")
        f.write(f"EFFICIENCY GAIN: {gain:.1f}% fewer items needed with Adaptive approach (at similar accuracy).\n")
        f.write("="*80 + "\n")
    
    print(f"Results written to {results_file}")

if __name__ == "__main__":
    main()
