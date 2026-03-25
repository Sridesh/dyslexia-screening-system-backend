from app.adaptive_testing_module import orchestration_engine, selection
import datetime

def test_engine():
    print("Testing backend processing loop...")
    
    start_time = datetime.datetime.now(datetime.timezone.utc)
    
    # Mock items
    module_item_ids = {
        "phonemic_awareness": [1, 2],
        "ran": [3, 4],
        "object_recognition": [5, 6]
    }
    
    item_pool = {
        1: selection.CandidateItem(1, "phonemic_awareness", -1.0, 1.0, 5.0),
        2: selection.CandidateItem(2, "phonemic_awareness", 1.0, 1.0, 5.0),
        3: selection.CandidateItem(3, "ran", -1.0, 1.0, 5.0),
        4: selection.CandidateItem(4, "ran", 1.0, 1.0, 5.0),
        5: selection.CandidateItem(5, "object_recognition", -1.0, 1.0, 5.0),
        6: selection.CandidateItem(6, "object_recognition", 1.0, 1.0, 5.0),
    }

    res = orchestration_engine.start_new_test(1, module_item_ids, item_pool, start_time)
    
    assert res.session is not None
    assert res.first_item is not None
    
    print("Start test successful.")
    
    # Process a few responses to trigger risk
    session = res.session
    item = res.first_item
    
    for i in range(15): # Trigger early stopping
        if item is None:
            break
        step_res = orchestration_engine.process_response(
            session=session,
            module_id=item.module_id,
            item=item,
            is_correct=True,
            rt_seconds=2.0,
            response_timestamp=start_time + datetime.timedelta(seconds=(i+1)*5),
            item_pool=item_pool
        )
        session = step_res.session
        item = step_res.next_item
        if step_res.should_stop:
            print(f"Risk calculated successfully! Category: {step_res.global_risk.risk_category}, Subtype: {step_res.global_risk.subtype}")
            break

    print("Backend End-to-End Test PASSED.")

if __name__ == "__main__":
    test_engine()
