from sqlalchemy.orm import Session
from app.models.test_item_log import TestItemLog
from app.schemas.test_item_log import TestItemLogCreate
from typing import List

def create_test_item_log(db: Session, log: TestItemLogCreate):
    db_log = TestItemLog(**log.model_dump())
    db.add(db_log)
    db.commit()
    db.refresh(db_log)
    return db_log

def get_logs_by_test(db: Session, test_id: int):
    return db.query(TestItemLog).filter(TestItemLog.test_id == test_id).all()
