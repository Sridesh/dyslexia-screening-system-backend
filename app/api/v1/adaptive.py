from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import Dict, Any, Optional
from datetime import datetime
from pydantic import BaseModel

from app import crud, schemas, models
from app.deps import deps
from app.adaptive_testing_module import orchestration_engine, selection, config
from app.services import test_service, items as items_service, results as results_service

router = APIRouter()

class StartTestRequest(BaseModel):
    child_id: int
    device_id: Optional[str] = None

@router.post("/tests/", response_model=Dict[str, Any]) # RESTful: /tests/ creates a test
def create_and_start_test(request: StartTestRequest, db: Session = Depends(deps.get_db)):
    """
    Create a new Test in DB and start the adaptive session.
    Returns the first item to administer.
    """
    # 1. Create Test row
    test_create = schemas.test.TestCreate(
        child_id=request.child_id,
        device_id=request.device_id,
        status="in_progress"
    )
    db_test_create_dict = test_create.model_dump()
    db_test_create_dict["start_time"] = datetime.utcnow()
    
    test = crud.test.create_test(db, schemas.test.TestCreate(**db_test_create_dict))
    
    # 2. Load Active Items & Build Pool using Service
    active_items = items_service.load_active_items(db)
    if not active_items:
         raise HTTPException(status_code=500, detail="No active items available")
         
    item_pool = items_service.build_item_pool(active_items)
    module_item_ids = items_service.build_module_item_ids(active_items)

    # 3. Call engine to start test
    try:
        result = orchestration_engine.start_new_test(
            test_id=test.id,
            module_item_ids=module_item_ids,
            item_pool=item_pool,
            started_at=test.start_time
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to initialize adaptive engine: {str(e)}")

    # 4. Save session snapshot
    test_service.save_session_snapshot(db, test, result.session)
    db.commit()

    # 5. Return first item with content
    if result.first_item:
        # Find the ORM item to return full content fields
        db_item = next((it for it in active_items if it.id == result.first_item.id), None)
        if not db_item:
             # Should not happen if pool consistent
             raise HTTPException(status_code=500, detail="Selected item not found in DB")
             
        return {
            "test_id": test.id,
            "first_item": item_to_response_dict(db_item)
        }
    else:
         return {
            "test_id": test.id,
            "message": "No items available",
            "active": False
        }

# Maintain legacy /start endpoint if needed, or route it to here?
# User prompt suggested `/tests/` for creation. I'll adhere to that for creation.
# But I should probably keep `/adaptive/start` redirecting or specific to adaptive if "Test" is generic.
# For now, I'll update the existing /start to align or replace. 
# "Start test route... In your POST /tests/ handler" -> implies generic test creation IS the start.
# I will expose this as /adaptive/start (legacy name from my prev steps) AND /tests/ (new suggestion)?
# Let's update the existing /adaptive/start to be clean and maybe alias /tests/ creation.
# But `app/api/v1/adaptive.py` is mounted at `/adaptive`, so `/adaptive/tests/`? No.
# I will keep it as `/adaptive/start` (or `/adaptive/tests` if creating). 
# User prompt: "3.1 Start test route... @router.post("/tests/")".
# I should probably respect the prompt's route naming if I can.
# But I am editing `app/api/v1/adaptive.py`. 
# I will rename the function to `create_test_endpoint` and path to `/` (so it becomes /adaptive/).
# OR I create a new router file `app/api/v1/tests.py`? 
# The user said "app/api/routes_tests.py".
# I'll stick to `adaptive.py` but update the path to `/{test_id}/start` OR just `/start` for creation?
# My previous implementation was `/start` creates a test.
# I will keep `/start` for creation to match "Start test route".

@router.post("/start", response_model=Dict[str, Any])
def start_test_endpoint(request: StartTestRequest, db: Session = Depends(deps.get_db)):
    return create_and_start_test(request, db)


@router.post("/{test_id}/submit", response_model=Dict[str, Any]) # Legacy path
@router.post("/{test_id}/responses", response_model=Dict[str, Any]) # Prompt path
def submit_response_endpoint(
    test_id: int, 
    # Payload structure differs: prompt uses raw dict, I verify with schema
    # prompt: payload: dict... item_id, is_correct, response_time_seconds
    # I'll use a Pydantic model that matches that for safety, or generic dict.
    # My `TestItemLogCreate` has these fields.
    response: schemas.test_item_log.TestItemLogCreate, # This fits well
    db: Session = Depends(deps.get_db)
):
    # 1. Load Test
    test = crud.test.get_test(db, test_id=test_id)
    if not test:
         raise HTTPException(status_code=404, detail="Test not found")
    
    if test.status == "completed":
        # Maybe allow idempotence or just return completed
        return {"status": "completed"}

    # 2. Load Session via Service
    try:
        session = test_service.load_session_state(test)
    except ValueError:
        raise HTTPException(status_code=400, detail="Test not started")

    # 3. Build Pool via Service
    # items_service.load_active_items(db) -> this fetches ALL items. Logic says "all active items".
    all_items = items_service.load_active_items(db)
    item_pool = items_service.build_item_pool(all_items)

    # 4. Identify Responded Item
    responded_item_cand = item_pool.get(response.item_id)
    if not responded_item_cand:
        raise HTTPException(status_code=400, detail="Invalid item_id submitted")

    # 5. Process logic
    result = orchestration_engine.process_response(
        session=session,
        module_id=responded_item_cand.module_id,
        item=responded_item_cand,
        is_correct=response.is_correct,
        rt_seconds=response.response_time_s,
        response_timestamp=datetime.utcnow(),
        item_pool=item_pool
    )

    # 6. Save Snapshot
    test_service.save_session_snapshot(db, test, result.session)
    
    # 7. Log Response (DB)
    crud.test_item_log.create_test_item_log(db, response)

    # 8. Check Stop
    if result.should_stop and result.global_risk:
        test.status = "completed"
        test.end_time = datetime.utcnow()
        test.total_time_s = session.total_time_seconds
        test.total_items = sum(getattr(m, 'num_items', 0) for m in session.modules.values())
        test.final_fatigue_level = config.MIN_FATIGUE_FACTOR
        
        # Save Results via Service
        results_service.save_test_results(db, test, result.global_risk, session.modules)
        
        # Update Test row
        test.final_risk_label = result.global_risk.risk_category
        test.final_risk_score = result.global_risk.risk_score
        test.final_risk_entropy = 1.0 - result.global_risk.confidence
        
        db.add(test)
        db.commit()

        return {
            "status": "completed",
            "risk": {
                 "category": result.global_risk.risk_category,
                 "score": result.global_risk.risk_score,
                 "confidence": result.global_risk.confidence,
                 "explanation": result.global_risk.explanation
            }
        }

    db.add(test)
    db.commit()

    # 9. Next Item
    if result.next_item:
        next_db_item = next((it for it in all_items if it.id == result.next_item.id), None)
        return {
            "status": "in_progress",
            "next_item": item_to_response_dict(next_db_item)
        }
    else:
        # Fallback if no item but not stopped (active pool exhaustion?)
        return {"status": "completed_fallback", "message": "No more items available"}

def item_to_response_dict(item_obj):
    # Manual dict or schema dump
    # Prompt asks for specific content fields
    return {
        "id": item_obj.id,
        "module_id": item_obj.module,
        "difficulty": item_obj.difficulty,
        "max_time_seconds": item_obj.max_time_s,
        "prompt_text": item_obj.prompt_text,
        "prompt_media": item_obj.prompt_media,
        "correct_option": item_obj.correct_option,
        "options_json": item_obj.options_json
    }
