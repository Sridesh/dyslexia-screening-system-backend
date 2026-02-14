from pydantic import BaseModel
from datetime import datetime
from typing import Optional

class ChildBase(BaseModel):
    external_id: Optional[str] = None
    name: Optional[str] = None
    dob: Optional[datetime] = None
    gender: Optional[str] = None
    language: Optional[str] = None
    notes: Optional[str] = None

class ChildCreate(ChildBase):
    pass

class ChildUpdate(ChildBase):
    pass

class Child(ChildBase):
    id: int
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None

    class Config:
        from_attributes = True
