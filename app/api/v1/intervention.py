from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.deps import deps
from app.services.intervention_agent import generate_intervention_plan

router = APIRouter()

@router.get("/{test_id}")
def get_intervention_plan(test_id: int, db: Session = Depends(deps.get_db)):
    """
    RAG-based endpoint: Generates an educational intervention plan based on the 
    child's specific risk profile, subtype, and feature contributions.
    """
    try:
        plan = generate_intervention_plan(db, test_id)
        return {"test_id": test_id, "intervention_plan": plan}
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail="Internal server error")
