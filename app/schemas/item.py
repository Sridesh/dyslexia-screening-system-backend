from pydantic import BaseModel
from datetime import datetime
from typing import Optional

class ItemBase(BaseModel):
    module: str
    difficulty: float
    max_time_s: Optional[float] = None
    prompt_text: Optional[str] = None
    prompt_media: Optional[str] = None
    is_active: bool = True

class ItemCreate(ItemBase):
    pass

class ItemUpdate(ItemBase):
    module: Optional[str] = None
    difficulty: Optional[float] = None

class Item(ItemBase):
    id: int
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None

    class Config:
        from_attributes = True
