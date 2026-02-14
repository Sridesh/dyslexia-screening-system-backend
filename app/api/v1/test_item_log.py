from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List

from app import crud
from app.schemas import test_item_log as log_schema
from app.deps import deps

router = APIRouter()

@router.post("/", response_model=log_schema.TestItemLog, status_code=status.HTTP_201_CREATED)
def create_test_item_log(log: log_schema.TestItemLogCreate, db: Session = Depends(deps.get_db)):
    return crud.test_item_log.create_test_item_log(db=db, log=log)

@router.get("/test/{test_id}", response_model=List[log_schema.TestItemLog])
def read_logs_by_test(test_id: int, db: Session = Depends(deps.get_db)):
    return crud.test_item_log.get_logs_by_test(db, test_id=test_id)
