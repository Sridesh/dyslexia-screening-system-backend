from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List

from app import crud
from app.schemas import child as child_schema
from app.deps import deps

router = APIRouter()

@router.post("/", response_model=child_schema.Child, status_code=status.HTTP_201_CREATED)
def create_child(child: child_schema.ChildCreate, db: Session = Depends(deps.get_db)):
    return crud.child.create_child(db=db, child=child)

@router.get("/", response_model=List[child_schema.Child])
def read_children(skip: int = 0, limit: int = 100, db: Session = Depends(deps.get_db)):
    children = crud.child.get_children(db, skip=skip, limit=limit)
    return children

@router.get("/{child_id}", response_model=child_schema.Child)
def read_child(child_id: int, db: Session = Depends(deps.get_db)):
    db_child = crud.child.get_child(db, child_id=child_id)
    if db_child is None:
        raise HTTPException(status_code=404, detail="Child not found")
    return db_child

@router.put("/{child_id}", response_model=child_schema.Child)
def update_child(child_id: int, child: child_schema.ChildUpdate, db: Session = Depends(deps.get_db)):
    db_child = crud.child.update_child(db, child_id=child_id, child=child)
    if db_child is None:
        raise HTTPException(status_code=404, detail="Child not found")
    return db_child

@router.delete("/{child_id}", response_model=child_schema.Child)
def delete_child(child_id: int, db: Session = Depends(deps.get_db)):
    db_child = crud.child.delete_child(db, child_id=child_id)
    if db_child is None:
        raise HTTPException(status_code=404, detail="Child not found")
    return db_child
