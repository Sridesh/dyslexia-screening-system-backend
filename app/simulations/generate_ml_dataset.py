import sys
import os
import random
import numpy as np
import pandas as pd
from datetime import datetime, timedelta
from collections import defaultdict

# Ensure app is in path if running directly
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..")))

from app.adaptive_testing_module import config, orchestration_engine, bayes, selection
from app.simulations.simulate_ef_ads import make_large_synthetic_item_bank, simulate_response_for_child, SyntheticChild

def generate_random_profile() -> SyntheticChild:
    # Randomly generate underlying theoretical abilities
    true_pa = random.uniform(-3.0, 3.0)
    true_ran = random.uniform(-3.0, 3.0)
    true_or = random.uniform(-3.0, 3.0)
    
    return SyntheticChild(
        name=f"Rand_{random.randint(1000,9999)}",
        theta_by_module={"phonemic_awareness": true_pa, "ran": true_ran, "object_recognition": true_or}
    )

def determine_ground_truth(child: SyntheticChild) -> int:
    # Ground truth: Child is "At Risk" if PA or RAN is significantly impaired
    # or if combined PA/RAN is low.
    pa = child.theta_by_module["phonemic_awareness"]
    ran = child.theta_by_module["ran"]
    
    if pa <= -1.2 or ran <= -1.2 or (pa + ran) <= -1.5:
        return 1
    return 0

def collect_test_features(test_id: int, child: SyntheticChild, item_pool, module_item_ids):
    start_time = datetime.now()
    start_result = orchestration_engine.start_new_test(
        test_id=test_id,
        module_item_ids=module_item_ids,
        item_pool=item_pool,
        started_at=start_time,
    )

    session = start_result.session
    current_item = start_result.first_item
    
    steps = 0
    max_steps = 150
    
    # Store RTs per module
    rt_sums = defaultdict(float)
    item_counts = defaultdict(int)

    while steps < max_steps:
        if current_item is None:
            break
        
        steps += 1
        is_correct, rt_seconds = simulate_response_for_child(child, current_item)
        
        rt_sums[current_item.module_id] += rt_seconds
        item_counts[current_item.module_id] += 1

        sim_time = start_time + timedelta(seconds=(steps * 5))
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
            break
        current_item = result.next_item

    # Extract final estimated Thetas
    estimated_thetas = {}
    for mid, m in session.modules.items():
        if sum(m.theta_posterior) > 0:
            est_theta = sum(p * t for p, t in zip(m.theta_posterior, config.THETA_GRID))
        else:
            est_theta = 0.0
        estimated_thetas[mid] = est_theta

    # Extract average RT for RAN
    avg_rt_ran = (rt_sums["ran"] / item_counts["ran"]) if item_counts["ran"] > 0 else 5.0

    return {
        "est_theta_pa": estimated_thetas.get("phonemic_awareness", 0.0),
        "est_theta_ran": estimated_thetas.get("ran", 0.0),
        "est_theta_or": estimated_thetas.get("object_recognition", 0.0),
        "avg_rt_ran": avg_rt_ran
    }

def main():
    random.seed(42)
    item_pool, module_item_ids = make_large_synthetic_item_bank()
    
    NUM_SAMPLES = 2000
    print(f"Generating {NUM_SAMPLES} synthetic child test sessions...")
    
    data_rows = []
    
    for i in range(NUM_SAMPLES):
        if (i+1) % 200 == 0:
            print(f"  Processed {i+1} / {NUM_SAMPLES} records...")
            
        child = generate_random_profile()
        ground_truth = determine_ground_truth(child)
        features = collect_test_features(i+1, child, item_pool, module_item_ids)
        
        features["is_at_risk"] = ground_truth
        data_rows.append(features)
        
    df = pd.DataFrame(data_rows)
    df.to_csv("synthetic_ml_dataset.csv", index=False)
    print("Saved dataset to synthetic_ml_dataset.csv")
    
    # Train ML Model
    print("\nTraining Logistic Regression Classifier...")
    from sklearn.linear_model import LogisticRegression
    from sklearn.model_selection import train_test_split
    from sklearn.metrics import classification_report
    
    X = df[['est_theta_pa', 'est_theta_ran', 'est_theta_or', 'avg_rt_ran']]
    y = df['is_at_risk']
    
    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)
    
    model = LogisticRegression(max_iter=1000)
    model.fit(X_train, y_train)
    
    y_pred = model.predict(X_test)
    print(classification_report(y_test, y_pred))
    
    # Extract Mathematical Weights
    print("="*60)
    print(" LOGISTIC REGRESSION WEIGHTS (FOR RISK.PY) ")
    print("="*60)
    print("Replace your hardcoded risk math with the following values:\n")
    print(f"w_pa         = {model.coef_[0][0]:.4f}")
    print(f"w_ran        = {model.coef_[0][1]:.4f}")
    print(f"w_or         = {model.coef_[0][2]:.4f}")
    print(f"w_rt_ran     = {model.coef_[0][3]:.4f}")
    print(f"bias / intc  = {model.intercept_[0]:.4f}")
    print("="*60)
    print("Formula: Probability = 1 / (1 + math.exp(-(bias + w_pa*PA + w_ran*RAN + w_or*OR + w_rt_ran*RT)))\n")

if __name__ == "__main__":
    main()
