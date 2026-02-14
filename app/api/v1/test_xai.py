from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List

from app import crud
from app.schemas import test_xai as xai_schema
from app.deps import deps

router = APIRouter()

@router.post("/", response_model=xai_schema.TestXAI, status_code=status.HTTP_201_CREATED)
def create_test_xai(xai: xai_schema.TestXAICreate, db: Session = Depends(deps.get_db)):
    return crud.test_xai.create_test_xai(db=db, xai=xai)

@router.get("/test/{test_id}", response_model=List[xai_schema.TestXAI])
def read_xai_by_test(test_id: int, db: Session = Depends(deps.get_db)):
    return crud.test_xai.get_xai_by_test(db, test_id=test_id)
