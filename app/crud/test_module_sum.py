from sqlalchemy.orm import Session
from app.models.test_module_sum import TestModuleSum
from app.schemas.test_module_sum import TestModuleSumCreate
from typing import List

def create_test_module_sum(db: Session, summary: TestModuleSumCreate):
    db_summary = TestModuleSum(**summary.model_dump())
    db.add(db_summary)
    db.commit()
    db.refresh(db_summary)
    return db_summary

def get_summaries_by_test(db: Session, test_id: int):
    return db.query(TestModuleSum).filter(TestModuleSum.test_id == test_id).all()
