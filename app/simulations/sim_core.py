import random
from datetime import datetime, timedelta
from typing import Dict, Any, List, Tuple
from app.adaptive_testing_module import bayes, orchestration_engine, risk
from app.adaptive_testing_module.selection import CandidateItem
from .profiles import SyntheticChild, PROFILES
from .item_bank import load_item_bank_from_csv

def simulate_response(child: SyntheticChild, item: CandidateItem, a_by_module: Dict[str, float]) -> Tuple[bool, float]:
    theta = child.theta_by_module.get(item.module_id, 0.0)
    a = a_by_module.get(item.module_id, 1.0)
    b = item.difficulty
    
    p_correct = bayes.prob_correct(theta, a, b)
    is_correct = random.random() < p_correct

    # Simple RT model: harder + incorrect = slower
    base_rt = item.max_time_seconds * 0.6
    diff_effect = abs(b - theta) * 0.5
    error_effect = 0.5 if not is_correct else 0.0
    noise = random.uniform(-0.5, 0.5)
    rt = max(0.5, base_rt + diff_effect + error_effect + noise)
    return is_correct, rt

def simulate_one_test(child: SyntheticChild, test_id: int) -> Dict[str, Any]:
    item_pool, module_item_ids = load_item_bank_from_csv()
    
    # Discrimination params roughly matching config.ITEM_DISCRIMINATION or tweaked
    a_by_module = {
        "phonemic_awareness": 1.4,
        "ran": 1.2,
        "object_recognition": 0.8,
    }

    start_time = datetime.utcnow()
    
    # Use orchestration engine to start test
    start_res = orchestration_engine.start_new_test(
        test_id=test_id,
        module_item_ids=module_item_ids,
        item_pool=item_pool,
        started_at=start_time,
    )
    
    session = start_res.session
    current_item = start_res.first_item
    global_risk = None
    step = 0
    max_steps = 100

    while current_item is not None and step < max_steps:
        step += 1
        is_correct, rt = simulate_response(child, current_item, a_by_module)
        
        result = orchestration_engine.process_response(
            session=session,
            module_id=current_item.module_id,
            item=current_item,
            is_correct=is_correct,
            rt_seconds=rt,
            response_timestamp=start_time + timedelta(seconds=step * 5),
            item_pool=item_pool,
        )
        
        session = result.session
        if result.should_stop:
            global_risk = result.global_risk
            break
            
        current_item = result.next_item

    # Fallback if loop ends without explicit stop triggering risk calc
    if global_risk is None:
        global_risk = risk.compute_global_risk(session)

    total_items = sum(m.num_items for m in session.modules.values())
    
    return {
        "risk_category": global_risk.risk_category,
        "risk_score": global_risk.risk_score,
        "total_items": total_items,
        # Potentially return module breakdown if needed
    }

def run_batch(num_runs_per_profile: int, seed: int = 42) -> Dict[str, Dict]:
    random.seed(seed)
    results: Dict[str, Dict] = {}
    test_id = 1

    for child in PROFILES:
        runs: List[Dict] = []
        for _ in range(num_runs_per_profile):
            r = simulate_one_test(child, test_id)
            runs.append(r)
            test_id += 1
            
        results[child.name] = {
            "ground_truth": child.ground_truth,
            "runs": runs,
        }
        
    return results
