from sqlalchemy.orm import Session
from app.models.child import Child
from app.schemas.child import ChildCreate, ChildUpdate
from typing import List, Optional

def get_child(db: Session, child_id: int):
    return db.query(Child).filter(Child.id == child_id).first()

def get_children(db: Session, skip: int = 0, limit: int = 100):
    return db.query(Child).offset(skip).limit(limit).all()

def create_child(db: Session, child: ChildCreate):
    db_child = Child(**child.model_dump())
    db.add(db_child)
    db.commit()
    db.refresh(db_child)
    return db_child

def update_child(db: Session, child_id: int, child: ChildUpdate):
    db_child = get_child(db, child_id)
    if not db_child:
        return None
    update_data = child.model_dump(exclude_unset=True)
    for key, value in update_data.items():
        setattr(db_child, key, value)
    db.add(db_child)
    db.commit()
    db.refresh(db_child)
    return db_child

def delete_child(db: Session, child_id: int):
    db_child = get_child(db, child_id)
    if not db_child:
        return None
    db.delete(db_child)
    db.commit()
    return db_child
