from pydantic import BaseModel
from datetime import datetime
from typing import Optional

class TestItemLogBase(BaseModel):
    test_id: int
    item_id: int
    round_number: Optional[int] = None
    within_round_idx: Optional[int] = None
    global_index: Optional[int] = None
    module: str
    difficulty: Optional[float] = None
    response: Optional[str] = None
    is_correct: Optional[bool] = None
    response_time_s: Optional[float] = None
    started_at: Optional[datetime] = None
    submitted_at: Optional[datetime] = None
    is_switch_question: bool = False
    was_slow_correct: bool = False
    fatigue_factor_used: Optional[float] = None
    p_module_weak_before: Optional[float] = None
    p_module_strong_before: Optional[float] = None
    p_module_weak_after: Optional[float] = None
    p_module_strong_after: Optional[float] = None
    p_risk_atrisk_before: Optional[float] = None
    p_risk_atrisk_after: Optional[float] = None

class TestItemLogCreate(TestItemLogBase):
    pass

class TestItemLog(TestItemLogBase):
    id: int
    created_at: Optional[datetime] = None

    class Config:
        from_attributes = True
