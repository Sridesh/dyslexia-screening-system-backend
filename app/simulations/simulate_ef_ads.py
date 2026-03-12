import sys
import os
import random
import numpy as np
from collections import defaultdict
from dataclasses import dataclass
from typing import Dict, List, Tuple, Optional
from datetime import datetime

# Ensure app is in path if running directly
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..")))

from app.adaptive_testing_module import config, state, bayes, selection, stopping, risk, orchestration_engine

# --------------------------------------------------------------------------
# 1. Scaled Synthetic Item Bank
# --------------------------------------------------------------------------
def make_large_synthetic_item_bank() -> Tuple[Dict[int, selection.CandidateItem], Dict[str, List[int]]]:
    items = {}
    item_id = 1
    
    # Create 50 items per module uniformly distributed from -3.0 to +3.0
    difficulties = np.linspace(-3.0, 3.0, 50)
    
    for module_id in config.MODULES: 
        for b in difficulties:
            items[item_id] = selection.CandidateItem(
                id=item_id,
                module_id=module_id,
                difficulty=float(b),
                max_time_seconds=random.uniform(3.0, 7.0), # Realistic variance in max time
            )
            item_id += 1

    module_item_ids = {}
    for item in items.values():
        module_item_ids.setdefault(item.module_id, []).append(item.id)

    return items, module_item_ids

# --------------------------------------------------------------------------
# 2. Comprehensive Synthetic Children Profiles
# --------------------------------------------------------------------------
@dataclass
class SyntheticChild:
    name: str
    theta_by_module: Dict[str, float]
    forced_slow_ran: bool = False

children = [
    SyntheticChild("Strong_All", {"phonemic_awareness": 1.5, "ran": 1.5, "object_recognition": 1.5}),
    SyntheticChild("Average_Kid", {"phonemic_awareness": 0.0, "ran": 0.0, "object_recognition": 0.0}),
    SyntheticChild("Borderline_All", {"phonemic_awareness": -0.3, "ran": -0.3, "object_recognition": -0.3}),
    SyntheticChild("PA_only_mild", {"phonemic_awareness": -0.8, "ran": 0.0, "object_recognition": 0.0}),
    SyntheticChild("PA_only_severe", {"phonemic_awareness": -1.5, "ran": 0.0, "object_recognition": 0.0}),
    SyntheticChild("RAN_only_mild", {"phonemic_awareness": 0.0, "ran": -0.8, "object_recognition": 0.0}),
    SyntheticChild("RAN_only_severe", {"phonemic_awareness": 0.0, "ran": -1.5, "object_recognition": 0.0}),
    SyntheticChild("Double_deficit_mild", {"phonemic_awareness": -0.8, "ran": -0.8, "object_recognition": 0.0}),
    SyntheticChild("Double_deficit_severe", {"phonemic_awareness": -1.5, "ran": -1.5, "object_recognition": 0.0}),
    SyntheticChild("Visual_primary", {"phonemic_awareness": 0.0, "ran": 0.0, "object_recognition": -1.2}),
    SyntheticChild("Slow_But_Accurate_RAN", {"phonemic_awareness": 0.0, "ran": 0.0, "object_recognition": 0.0}, forced_slow_ran=True),
]

# --------------------------------------------------------------------------
# 3. True 4PL Response Simulation
# --------------------------------------------------------------------------
def simulate_response_for_child(child: SyntheticChild, item: selection.CandidateItem) -> Tuple[bool, float]:
    theta = child.theta_by_module.get(item.module_id, 0.0)
    a = config.ITEM_DISCRIMINATION.get(item.module_id, 1.0)
    c = config.ITEM_GUESSING.get(item.module_id, 0.0)
    d = config.ITEM_SLIPPING.get(item.module_id, 0.0)
    b = item.difficulty

    # Use the 4PL model to accurately simulate the child's response
    p_correct = bayes.prob_correct(theta, a, b, c, d)
    is_correct = random.random() < p_correct

    # RT Model: Slower RT if the question is hard for them, noisy otherwise
    base_rt = item.max_time_seconds * 0.5
    difficulty_effect = max(0, b - theta) * 1.5 
    noise = random.uniform(-1.0, 1.0)
    
    rt_seconds = max(1.0, base_rt + difficulty_effect + noise)
    
    if child.forced_slow_ran and item.module_id == "ran":
        rt_seconds += 6.0 # Force an artificially slow reaction time
        
    # Ensure they don't take longer than technically allowed for the sake of the sim
    rt_seconds = min(rt_seconds, item.max_time_seconds + 5.0) 

    return is_correct, rt_seconds

# --------------------------------------------------------------------------
# 4. Engine Execution
# --------------------------------------------------------------------------
def simulate_single_test(child: SyntheticChild, test_id: int):
    item_pool, module_item_ids = make_large_synthetic_item_bank()
    import datetime
    start_time = datetime.datetime.now(datetime.timezone.utc)

    start_result = orchestration_engine.start_new_test(
        test_id=test_id,
        module_item_ids=module_item_ids,
        item_pool=item_pool,
        started_at=start_time,
    )

    session = start_result.session
    current_item = start_result.first_item
    global_risk = None
    steps = 0
    max_steps = 150 # Absolute safety break
    
    while steps < max_steps:
        if current_item is None:
            break
        
        steps += 1
        is_correct, rt_seconds = simulate_response_for_child(child, current_item)

        import datetime
        sim_time = start_time + datetime.timedelta(seconds=(steps * 5)) # Simulate passage of time

        result = orchestration_engine.process_response(
            session=session,
            module_id=current_item.module_id,
            item=current_item,
            is_correct=is_correct,
            rt_seconds=rt_seconds,
            response_timestamp=sim_time,
            item_pool=item_pool,
        )

        session = result.session
        if result.should_stop:
            global_risk = result.global_risk
            break
        current_item = result.next_item

    if not global_risk and session.stopped:
         global_risk = risk.compute_global_risk(session)

    # Extract final estimated Thetas
    estimated_thetas = {}
    for mid, m in session.modules.items():
        # The expected value of theta given the posterior
        est_theta = sum(p * t for p, t in zip(m.theta_posterior, config.THETA_GRID))
        estimated_thetas[mid] = est_theta

    return {
        "child_name": child.name,
        "total_items": sum(m.num_items for m in session.modules.values()),
        "total_time_s": session.total_time_seconds,
        "global_risk": global_risk,
        "subtype": global_risk.subtype if global_risk else "None",
        "estimated_thetas": estimated_thetas
    }

# --------------------------------------------------------------------------
# 5. Statistical Aggregation & Reporting
# --------------------------------------------------------------------------
def summarize_results(results):
    stats = defaultdict(lambda: {
        "n": 0, "sum_items": 0, "sum_time": 0.0, 
        "risk_counts": defaultdict(int),
        "theta_errors": defaultdict(list)
    })

    # Find the original child objects to look up true Thetas
    child_map = {c.name: c for c in children}

    for r in results:
        c = r["child_name"]
        stats[c]["n"] += 1
        stats[c]["sum_items"] += r["total_items"]
        stats[c]["sum_time"] += r["total_time_s"]
        
        risk_cat = r["global_risk"].risk_category if r["global_risk"] else "None"
        subtype = r["subtype"]
        stats[c]["risk_counts"][risk_cat] += 1
        stats[c]["risk_counts"][f"Subtype: {subtype}"] += 1
        
        true_thetas = child_map[c].theta_by_module
        for mid, est_t in r["estimated_thetas"].items():
            true_t = true_thetas.get(mid, 0.0)
            error = est_t - true_t
            stats[c]["theta_errors"][mid].append(error)

    print("\n" + "="*80)
    print(" COMPREHENSIVE 4PL SIMULATION RESULTS ")
    print("="*80)
    
    for child_name, s in stats.items():
        n = s["n"]
        print(f"\n[ PROFILE ]: {child_name}")
        
        true_t = child_map[child_name].theta_by_module
        print(f"  True Thetas : PA={true_t['phonemic_awareness']:+1.1f} | RAN={true_t['ran']:+1.1f} | OR={true_t['object_recognition']:+1.1f}")
        
        print(f"  - Runs: {n}")
        print(f"  - Avg Items Asked: {s['sum_items'] / n:.1f} questions")
        print("  - Risk Distribution:")
        for cat, count in s["risk_counts"].items():
            print(f"      {cat:<10}: {count} ({count / n:.1%})")
            
        print("  - Average Engine Error (Est. Theta - True Theta):")
        for mid, errs in s["theta_errors"].items():
            mean_err = np.mean(errs)
            std_err = np.std(errs)
            print(f"      {mid:<20}: Mean Error = {mean_err:+0.2f} (±{std_err:0.2f})")

def run_simulations(num_runs: int = 50):
    random.seed(42) # Deterministic for consistent baseline
    
    results = []
    test_id_counter = 1
    
    print(f"\nBooting up massive simulation...")
    print(f"Profiles: {len(children)}")
    print(f"Runs per profile: {num_runs}")
    print(f"Total simulated tests: {len(children) * num_runs}\n")
    
    for idx, child in enumerate(children):
        print(f"[{idx+1}/{len(children)}] Simulating {child.name}...", end=" ", flush=True)
        for _ in range(num_runs):
            results.append(simulate_single_test(child, test_id=test_id_counter))
            test_id_counter += 1
        print("Done.")
            
    summarize_results(results)

if __name__ == "__main__":
    run_simulations()
