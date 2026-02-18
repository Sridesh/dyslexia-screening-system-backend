from sqlalchemy import Column, Integer, String, Boolean, Float, Text, DateTime
from sqlalchemy.orm import relationship
from app.db.database import Base

class Item(Base):
    __tablename__ = "item"

    id = Column(Integer, primary_key=True, index=True)
    module = Column(String, index=True, nullable=False)     # e.g. "RAN"
    difficulty = Column(Float, nullable=False)
    max_time_s = Column(Float, nullable=True)
    prompt_text = Column(Text, nullable=True)
    prompt_media = Column(String, nullable=True)
    correct_option = Column(String, nullable=True)
    options_json = Column(Text, nullable=True) # JSON string of options
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, nullable=True)
    updated_at = Column(DateTime, nullable=True)

    logs = relationship("TestItemLog", back_populates="item")
