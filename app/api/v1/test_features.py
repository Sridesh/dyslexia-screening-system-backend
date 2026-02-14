from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import Optional

from app import crud
from app.schemas import test_features as feat_schema
from app.deps import deps

router = APIRouter()

@router.post("/", response_model=feat_schema.TestFeatures, status_code=status.HTTP_201_CREATED)
def create_test_features(features: feat_schema.TestFeaturesCreate, db: Session = Depends(deps.get_db)):
    return crud.test_features.create_test_features(db=db, features=features)

@router.get("/test/{test_id}", response_model=feat_schema.TestFeatures)
def read_features_by_test(test_id: int, db: Session = Depends(deps.get_db)):
    features = crud.test_features.get_features_by_test(db, test_id=test_id)
    if features is None:
        raise HTTPException(status_code=404, detail="Features not found for this test")
    return features
