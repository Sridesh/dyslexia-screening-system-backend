from pydantic import BaseModel
from datetime import datetime
from typing import Optional

class TestModuleSumBase(BaseModel):
    test_id: int
    module: str
    p_weak_final: Optional[float] = None
    p_strong_final: Optional[float] = None
    entropy_final: Optional[float] = None
    num_items: Optional[int] = None
    avg_time_s: Optional[float] = None
    min_time_s: Optional[float] = None
    max_time_s: Optional[float] = None
    slow_correct_count: Optional[int] = None
    total_correct_count: Optional[int] = None
    slow_correct_ratio: Optional[float] = None
    avg_switch_rt_s: Optional[float] = None
    switch_count: Optional[int] = None
    first_round_seen: Optional[int] = None
    last_round_seen: Optional[int] = None

class TestModuleSumCreate(TestModuleSumBase):
    pass

class TestModuleSum(TestModuleSumBase):
    id: int
    created_at: Optional[datetime] = None

    class Config:
        from_attributes = True
