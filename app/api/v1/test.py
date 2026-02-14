from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List, Optional

from app import crud
from app.schemas import test as test_schema
from app.deps import deps

router = APIRouter()

@router.post("/", response_model=test_schema.Test, status_code=status.HTTP_201_CREATED)
def create_test(test: test_schema.TestCreate, db: Session = Depends(deps.get_db)):
    return crud.test.create_test(db=db, test=test)

@router.get("/", response_model=List[test_schema.Test])
def read_tests(skip: int = 0, limit: int = 100, child_id: Optional[int] = None, db: Session = Depends(deps.get_db)):
    tests = crud.test.get_tests(db, skip=skip, limit=limit, child_id=child_id)
    return tests

@router.get("/{test_id}", response_model=test_schema.Test)
def read_test(test_id: int, db: Session = Depends(deps.get_db)):
    db_test = crud.test.get_test(db, test_id=test_id)
    if db_test is None:
        raise HTTPException(status_code=404, detail="Test not found")
    return db_test

@router.put("/{test_id}", response_model=test_schema.Test)
def update_test(test_id: int, test: test_schema.TestUpdate, db: Session = Depends(deps.get_db)):
    db_test = crud.test.update_test(db, test_id=test_id, test=test)
    if db_test is None:
        raise HTTPException(status_code=404, detail="Test not found")
    return db_test
