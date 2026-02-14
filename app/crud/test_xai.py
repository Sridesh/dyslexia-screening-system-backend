from sqlalchemy.orm import Session
from app.models.test_xai import TestXAI
from app.schemas.test_xai import TestXAICreate
from typing import List

def create_test_xai(db: Session, xai: TestXAICreate):
    db_xai = TestXAI(**xai.model_dump())
    db.add(db_xai)
    db.commit()
    db.refresh(db_xai)
    return db_xai

def get_xai_by_test(db: Session, test_id: int):
    return db.query(TestXAI).filter(TestXAI.test_id == test_id).all()
