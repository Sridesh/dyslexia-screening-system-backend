from pydantic import BaseModel
from datetime import datetime
from typing import Optional

class TestFeaturesBase(BaseModel):
    test_id: int
    p_risk_atrisk: Optional[float] = None
    risk_entropy: Optional[float] = None
    total_items: Optional[int] = None
    total_time_s: Optional[float] = None
    final_fatigue: Optional[float] = None
    
    # Per-module simplified for schema, could be dynamic or specific
    p_weak_RAN: Optional[float] = None
    entropy_RAN: Optional[float] = None
    num_items_RAN: Optional[int] = None
    avg_time_RAN: Optional[float] = None
    slow_corr_ratio_RAN: Optional[float] = None
    avg_switch_rt_RAN: Optional[float] = None

    p_weak_phonology: Optional[float] = None
    entropy_phonology: Optional[float] = None
    num_items_phonology: Optional[int] = None
    avg_time_phonology: Optional[float] = None
    slow_corr_ratio_phonology: Optional[float] = None
    avg_switch_rt_phonology: Optional[float] = None

class TestFeaturesCreate(TestFeaturesBase):
    pass

class TestFeatures(TestFeaturesBase):
    created_at: Optional[datetime] = None

    class Config:
        from_attributes = True
