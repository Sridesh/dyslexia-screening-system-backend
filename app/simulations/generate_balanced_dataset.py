import sys
import os
import random
import pandas as pd
from datetime import datetime

# Ensure app is in path if running directly BEFORE importing app modules
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..")))
from app.simulations.master_validation_suite import SyntheticChild, make_synthetic_item_bank, run_single_simulation
from app.adaptive_testing_module import orchestration_engine, config

# ==============================================================================
# BALANCE MATRIX GENERATORS
# ==============================================================================

def generate_normal_profile(idx: int) -> SyntheticChild:
    pa = random.uniform(-0.7, 3.0)
    ran = random.uniform(-0.7, 3.0)
    or_val = random.uniform(-0.7, 3.0)
    return SyntheticChild(f"Normal_{idx}", {"phonemic_awareness": pa, "ran": ran, "object_recognition": or_val}, ground_truth=0)

def generate_pa_deficit_profile(idx: int) -> SyntheticChild:
    pa = random.uniform(-3.0, -1.2)
    ran = random.uniform(-0.5, 3.0)
    or_val = random.uniform(-0.5, 3.0)
    return SyntheticChild(f"PADef_{idx}", {"phonemic_awareness": pa, "ran": ran, "object_recognition": or_val}, ground_truth=1)

def generate_ran_deficit_profile(idx: int) -> SyntheticChild:
    pa = random.uniform(-0.5, 3.0)
    ran = random.uniform(-3.0, -1.2)
    or_val = random.uniform(-0.5, 3.0)
    
    forced_slow = random.choice([True, False])
    if forced_slow:
        ran = random.uniform(-0.5, 1.0) 
        
    return SyntheticChild(f"RANDef_{idx}", {"phonemic_awareness": pa, "ran": ran, "object_recognition": or_val}, ground_truth=1, forced_slow_ran=forced_slow)

def generate_double_deficit_profile(idx: int) -> SyntheticChild:
    pa = random.uniform(-3.0, -1.2)
    ran = random.uniform(-3.0, -1.2)
    or_val = random.uniform(-0.5, 3.0)
    return SyntheticChild(f"DblDef_{idx}", {"phonemic_awareness": pa, "ran": ran, "object_recognition": or_val}, ground_truth=1)


# ==============================================================================
# ML FEATURE COLLECTOR (Reusing master_validation_suite engine)
# ==============================================================================

from app.simulations.master_validation_suite import simulate_response
from datetime import timedelta, timezone

def collect_ml_features_via_engine(child: SyntheticChild, test_id: int, item_pool, module_item_ids) -> dict:
    start_time = datetime.now(timezone.utc)
    res = orchestration_engine.start_new_test(test_id, module_item_ids, item_pool, start_time)

    session = res.session
    current_item = res.first_item
    steps = 0
    
    # Track RT specifically for ML logic
    ran_rt_sum = 0.0
    ran_items = 0
    
    while current_item is not None and steps < 150:
        steps += 1
        is_correct, rt_seconds = simulate_response(child, current_item)
        sim_time = start_time + timedelta(seconds=(steps * 5))
        
        if current_item.module_id == "ran":
            ran_rt_sum += rt_seconds
            ran_items += 1

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
            break
        current_item = step_res.next_item

    # Extract exactly what risk.py sees
    est_thetas = {}
    for mid, m in session.modules.items():
        if sum(m.theta_posterior) > 0:
            est_thetas[mid] = sum(p * t for p, t in zip(m.theta_posterior, config.THETA_GRID))
        else:
            est_thetas[mid] = 0.0
            
    avg_rt_ran = (ran_rt_sum / ran_items) if ran_items > 0 else 5.0

    return {
        "est_theta_pa": est_thetas.get("phonemic_awareness", 0.0),
        "est_theta_ran": est_thetas.get("ran", 0.0),
        "est_theta_or": est_thetas.get("object_recognition", 0.0),
        "avg_rt_ran": avg_rt_ran,
        "is_at_risk": child.ground_truth
    }


def main():
    print("Initializing Balanced Clinical Matrix Generation...")
    NUM_PER_BUCKET = 2500
    profiles: list[SyntheticChild] = []
    
    for i in range(NUM_PER_BUCKET):
        profiles.append(generate_normal_profile(i))
        profiles.append(generate_pa_deficit_profile(i))
        profiles.append(generate_ran_deficit_profile(i))
        profiles.append(generate_double_deficit_profile(i))
        
    random.shuffle(profiles)
    item_pool, module_item_ids = make_synthetic_item_bank()
    
    print(f"Generated {len(profiles)} balanced synthetic profiles.")
    print("Commencing massive 4PL simulation sweep for ML Training...")
    
    data_rows = []
    for idx, child in enumerate(profiles):
        if (idx+1) % 500 == 0:
            print(f"  Processed {idx+1} / 10000 tests...")
            
        features = collect_ml_features_via_engine(child, idx, item_pool, module_item_ids)
        data_rows.append(features)
        
    df = pd.DataFrame(data_rows)
    df.to_csv("stratified_ml_dataset.csv", index=False)
    
    print("Simulation complete! Dataset explicitly balanced across clinical manifestations.")
    print("Saved -> stratified_ml_dataset.csv")

if __name__ == "__main__":
    main()
