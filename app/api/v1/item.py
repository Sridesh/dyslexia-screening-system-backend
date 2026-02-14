from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List

from app import crud
from app.schemas import item as item_schema
from app.deps import deps

router = APIRouter()

@router.post("/", response_model=item_schema.Item, status_code=status.HTTP_201_CREATED)
def create_item(item: item_schema.ItemCreate, db: Session = Depends(deps.get_db)):
    return crud.item.create_item(db=db, item=item)

@router.get("/", response_model=List[item_schema.Item])
def read_items(skip: int = 0, limit: int = 100, db: Session = Depends(deps.get_db)):
    items = crud.item.get_items(db, skip=skip, limit=limit)
    return items

@router.get("/{item_id}", response_model=item_schema.Item)
def read_item(item_id: int, db: Session = Depends(deps.get_db)):
    db_item = crud.item.get_item(db, item_id=item_id)
    if db_item is None:
        raise HTTPException(status_code=404, detail="Item not found")
    return db_item

@router.put("/{item_id}", response_model=item_schema.Item)
def update_item(item_id: int, item: item_schema.ItemUpdate, db: Session = Depends(deps.get_db)):
    db_item = crud.item.update_item(db, item_id=item_id, item=item)
    if db_item is None:
        raise HTTPException(status_code=404, detail="Item not found")
    return db_item

@router.delete("/{item_id}", response_model=item_schema.Item)
def delete_item(item_id: int, db: Session = Depends(deps.get_db)):
    db_item = crud.item.delete_item(db, item_id=item_id)
    if db_item is None:
        raise HTTPException(status_code=404, detail="Item not found")
    return db_item
