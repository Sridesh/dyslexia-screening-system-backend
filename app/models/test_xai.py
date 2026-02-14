from sqlalchemy import Column, Integer, String, Text, DateTime, ForeignKey
from sqlalchemy.orm import relationship
from app.db.database import Base

class TestXAI(Base):
    __tablename__ = "test_xai"

    id = Column(Integer, primary_key=True, index=True)
    test_id = Column(Integer, ForeignKey("test.id"), nullable=False)

    method = Column(String, nullable=False)      # e.g. "SHAP", "DiCE"
    payload_json = Column(Text, nullable=False)  # raw JSON string
    created_at = Column(DateTime, nullable=True)

    test = relationship("Test", back_populates="xai_records")
