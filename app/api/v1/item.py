from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List

from app import crud, models, schemas
from app.deps import deps

router = APIRouter()

@router.post("/", response_model=schemas.item.Item)
def create_item(item: schemas.item.ItemCreate, db: Session = Depends(deps.get_db)):
    return crud.item.create_item(db=db, item=item)

@router.get("/", response_model=List[schemas.item.Item])
def read_items(skip: int = 0, limit: int = 100, db: Session = Depends(deps.get_db)):
    items = crud.item.get_items(db, skip=skip, limit=limit)
    return items
