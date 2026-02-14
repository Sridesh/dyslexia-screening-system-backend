from sqlalchemy.orm import Session
from app.models.test import Test
from app.schemas.test import TestCreate, TestUpdate
from typing import List, Optional

def get_test(db: Session, test_id: int):
    return db.query(Test).filter(Test.id == test_id).first()

def get_tests(db: Session, skip: int = 0, limit: int = 100, child_id: Optional[int] = None):
    query = db.query(Test)
    if child_id:
        query = query.filter(Test.child_id == child_id)
    return query.offset(skip).limit(limit).all()

def create_test(db: Session, test: TestCreate):
    db_test = Test(**test.model_dump())
    db.add(db_test)
    db.commit()
    db.refresh(db_test)
    return db_test

def update_test(db: Session, test_id: int, test: TestUpdate):
    db_test = get_test(db, test_id)
    if not db_test:
        return None
    update_data = test.model_dump(exclude_unset=True)
    for key, value in update_data.items():
        setattr(db_test, key, value)
    db.add(db_test)
    db.commit()
    db.refresh(db_test)
    return db_test
