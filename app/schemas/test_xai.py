from pydantic import BaseModel
from datetime import datetime
from typing import Optional

class TestXAIBase(BaseModel):
    test_id: int
    method: str
    payload_json: str

class TestXAICreate(TestXAIBase):
    pass

class TestXAI(TestXAIBase):
    id: int
    created_at: Optional[datetime] = None

    class Config:
        from_attributes = True
