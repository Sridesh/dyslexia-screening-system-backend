from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List

from app import crud
from app.schemas import test_module_sum as sum_schema
from app.deps import deps

router = APIRouter()

@router.post("/", response_model=sum_schema.TestModuleSum, status_code=status.HTTP_201_CREATED)
def create_test_module_sum(summary: sum_schema.TestModuleSumCreate, db: Session = Depends(deps.get_db)):
    return crud.test_module_sum.create_test_module_sum(db=db, summary=summary)

@router.get("/test/{test_id}", response_model=List[sum_schema.TestModuleSum])
def read_summaries_by_test(test_id: int, db: Session = Depends(deps.get_db)):
    return crud.test_module_sum.get_summaries_by_test(db, test_id=test_id)
