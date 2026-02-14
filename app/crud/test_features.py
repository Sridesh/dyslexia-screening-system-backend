from sqlalchemy.orm import Session
from app.models.test_features import TestFeatures
from app.schemas.test_features import TestFeaturesCreate
from typing import Optional

def create_test_features(db: Session, features: TestFeaturesCreate):
    db_features = TestFeatures(**features.model_dump())
    db.add(db_features)
    db.commit()
    db.refresh(db_features)
    return db_features

def get_features_by_test(db: Session, test_id: int):
    return db.query(TestFeatures).filter(TestFeatures.test_id == test_id).first()
