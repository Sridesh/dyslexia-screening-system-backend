import sys
import os
import random
from collections import defaultdict
from dataclasses import dataclass
from typing import Dict, List, Tuple, Optional
from datetime import datetime

# Ensure app is in path if running directly
sys.path.append(os.getcwd())

from app.adaptive_testing_module import config, state, bayes, selection, stopping, risk, orchestration_engine

# --------------------------------------------------------------------------
# 1. Synthetic Item Bank
# --------------------------------------------------------------------------

def make_synthetic_item_bank() -> Tuple[Dict[int, selection.CandidateItem], Dict[str, List[int]]]:
    items = {}
    item_id = 1
    
    # Create valid modules from config to ensure match
    for module_id in config.MODULES: 
        # Create items across difficulty range
        for b in [-2.0, -1.0, 0.0, 1.0, 2.0]:
            # Create duplicates to have a larger pool? 
            # User example was simple loop. Let's add a few variations or just 1 per level per module?
            # User said: "For module in ... for b in ... items[item_id] = ..."
            # That results in 5 items per module.
            # config.MIN_ITEMS_PER_MODULE is 4. So 5 is just enough to test stopping.
            # Let's add 2 items per difficulty level to ensure we don't run out too fast 
            # and test stopping rules properly (sometimes need more evidence).
            for _ in range(2): 
                items[item_id] = selection.CandidateItem(
                    id=item_id,
                    module_id=module_id,
                    difficulty=b,
                    max_time_seconds=5.0,
                )
                item_id += 1

    module_item_ids = {}
    for item in items.values():
        module_item_ids.setdefault(item.module_id, []).append(item.id)

    return items, module_item_ids

# --------------------------------------------------------------------------
# 2. Synthetic Children
# --------------------------------------------------------------------------

@dataclass
class SyntheticChild:
    name: str
    theta_by_module: Dict[str, float]

children = [
    SyntheticChild(
        name="Strong_all",
        theta_by_module={
            "phonemic_awareness": 1.5,
            "ran": 1.5,
            "object_recognition": 1.0,
        },
    ),
    SyntheticChild(
        name="Weak_PA_RAN",
        theta_by_module={
            "phonemic_awareness": -1.5,
            "ran": -1.5,
            "object_recognition": 0.0,
        },
    ),
    SyntheticChild(
        name="Weak_RAN_only",
        theta_by_module={
            "phonemic_awareness": 0.5,
            "ran": -1.5,
            "object_recognition": 0.0,
        },
    ),
    SyntheticChild(
        name="Average_Kid",
        theta_by_module={
            "phonemic_awareness": 0.0,
            "ran": 0.0,
            "object_recognition": 0.0,
        },
    ),
]

# --------------------------------------------------------------------------
# 3. Simulate Response
# --------------------------------------------------------------------------

def simulate_response_for_child(child: SyntheticChild, item: selection.CandidateItem) -> Tuple[bool, float]:
    theta = child.theta_by_module.get(item.module_id, 0.0) # Fallback if missing
    a = config.ITEM_DISCRIMINATION.get(item.module_id, 1.0)
    b = item.difficulty

    p_correct = bayes.prob_correct(theta, a, b)
    is_correct = random.random() < p_correct

    # Simple RT model
    base_rt = item.max_time_seconds * 0.6
    noise = random.uniform(-0.5, 0.5)
    difficulty_effect = abs(b - theta) * 0.5
    correctness_effect = 0.5 if not is_correct else 0.0
    # Add a small randomness for "slow" children?
    # For now, stick to user's simple model
    rt_seconds = max(0.5, base_rt + difficulty_effect + correctness_effect + noise)

    return is_correct, rt_seconds

# --------------------------------------------------------------------------
# 4. Simulate Single Test
# --------------------------------------------------------------------------

def simulate_single_test(child: SyntheticChild, test_id: int):
    # Fresh item bank for each test (conceptually, though candidate items are immutable-ish)
    # But module_item_ids needs to be valid.
    item_pool, module_item_ids = make_synthetic_item_bank()
    start_time = datetime.utcnow()

    # 1. Start
    start_result = orchestration_engine.start_new_test(
        test_id=test_id,
        module_item_ids=module_item_ids,
        item_pool=item_pool,
        started_at=start_time,
    )

    session = start_result.session
    current_item = start_result.first_item
    
    # Global risk result container
    global_risk = None

    steps = 0
    max_steps = 100 # Safety break
    
    while steps < max_steps:
        if current_item is None:
            # Should have stopped or we ran out
            break
        
        steps += 1

        # 2. Child responds
        is_correct, rt_seconds = simulate_response_for_child(child, current_item)

        # 3. Process response
        result = orchestration_engine.process_response(
            session=session,
            module_id=current_item.module_id,
            item=current_item,
            is_correct=is_correct,
            rt_seconds=rt_seconds,
            response_timestamp=datetime.utcnow(),
            item_pool=item_pool,
        )

        session = result.session

        if result.should_stop:
            global_risk = result.global_risk
            break

        current_item = result.next_item

    # If loop finished without stop (e.g. max steps or None item returned without stop flag?)
    # The engine should handle stopping. If next_item is None, it usually sets stop=True inside engine.
    # We'll check session.stopped just in case.
    if not global_risk and session.stopped:
         global_risk = risk.compute_global_risk(session)

    # Collect outputs
    total_items = sum(m.num_items for m in session.modules.values())
    total_time_s = session.total_time_seconds
    
    return {
        "child_name": child.name,
        "total_items": total_items,
        "total_time_s": total_time_s,
        "global_risk": global_risk,
        "module_details": {
            mid: {
                "label": m.p_weak > m.p_strong and "weak" or "strong", # simple peek
                "p_weak": m.p_weak
            } for mid, m in session.modules.items()
        }
    }

# --------------------------------------------------------------------------
# 5. Run & Aggregation
# --------------------------------------------------------------------------

def summarize_results(results):
    stats = defaultdict(lambda: {"n": 0, "sum_items": 0, "sum_time": 0.0, "risk_counts": defaultdict(int)})

    for r in results:
        c = r["child_name"]
        stats[c]["n"] += 1
        stats[c]["sum_items"] += r["total_items"]
        stats[c]["sum_time"] += r["total_time_s"]
        
        risk_cat = "None"
        if r["global_risk"]:
            risk_cat = r["global_risk"].risk_category
        stats[c]["risk_counts"][risk_cat] += 1

    print("\n" + "="*60)
    print("SIMULATION RESULTS")
    print("="*60)
    
    for child_name, s in stats.items():
        n = s["n"]
        print(f"\nChild profile: {child_name}")
        print(f"  Runs: {n}")
        print(f"  Avg items: {s['sum_items'] / n:.2f}")
        print(f"  Avg time (s): {s['sum_time'] / n:.2f}")
        print("  Risk Distribution:")
        for cat, count in s["risk_counts"].items():
            print(f"    {cat:<10}: {count} ({count / n:.2%})")

def run_simulations(num_runs: int = 5):
    # random.seed(42) # Deterministic for testing? Or random for Monte Carlo?
    # User said "Run each child many times... to see average behavior".
    # Letting it be random is better for 'simulation', but let's seed for reproducibility validation.
    random.seed(42)
    
    results = []
    test_id_counter = 1
    
    print(f"Running simulation: {len(children)} profiles x {num_runs} runs...")
    
    for child in children:
        for _ in range(num_runs):
            print(f"  Simulating {child.name} run {_ + 1}/{num_runs}...", end="", flush=True)
            r = simulate_single_test(child, test_id=test_id_counter)
            print(" Done.")
            results.append(r)
            test_id_counter += 1
            
    summarize_results(results)

if __name__ == "__main__":
    run_simulations()
