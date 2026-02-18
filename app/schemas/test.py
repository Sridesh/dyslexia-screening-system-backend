from pydantic import BaseModel
from datetime import datetime
from typing import Optional, List

# Forward references
# from .test_item_log import TestItemLog
# from .test_module_sum import TestModuleSum
# from .test_features import TestFeatures
# from .test_xai import TestXAI

class TestBase(BaseModel):
    child_id: Optional[int] = None
    start_time: Optional[datetime] = None
    end_time: Optional[datetime] = None
    final_risk_label: Optional[str] = None
    final_risk_score: Optional[float] = None
    final_risk_entropy: Optional[float] = None
    total_items: Optional[int] = None
    total_time_s: Optional[float] = None
    final_fatigue_level: Optional[float] = None
    device_id: Optional[str] = None
    version: Optional[str] = None
    notes: Optional[str] = None
    session_state: Optional[str] = None
    status: Optional[str] = None

class TestCreate(TestBase):
    pass

class TestUpdate(TestBase):
    pass

class Test(TestBase):
    id: int
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None

    class Config:
        from_attributes = True
