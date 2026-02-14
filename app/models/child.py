from sqlalchemy import Column, Integer, String, DateTime, Text
from sqlalchemy.orm import relationship
from app.db.database import Base

class Child(Base):
    __tablename__ = "child"

    id = Column(Integer, primary_key=True, index=True)
    external_id = Column(String, index=True, nullable=True)
    name = Column(String, nullable=True)
    dob = Column(DateTime, nullable=True)
    gender = Column(String, nullable=True)
    language = Column(String, nullable=True)
    notes = Column(Text, nullable=True)
    created_at = Column(DateTime, nullable=True)
    updated_at = Column(DateTime, nullable=True)

    tests = relationship("Test", back_populates="child")
