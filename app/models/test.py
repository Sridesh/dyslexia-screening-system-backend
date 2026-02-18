from sqlalchemy import Column, Integer, String, Float, Text, DateTime, ForeignKey, JSON
from sqlalchemy.orm import relationship
from app.db.database import Base
from datetime import datetime

class Test(Base):
    __tablename__ = "test"

    id = Column(Integer, primary_key=True, index=True)
    child_id = Column(Integer, ForeignKey("child.id"), nullable=True)
    start_time = Column(DateTime, nullable=True, default=datetime.utcnow)
    end_time = Column(DateTime, nullable=True)

    final_risk_label = Column(String, nullable=True)   # "At-Risk"/"Not-At-Risk"
    final_risk_score = Column(Float, nullable=True)    # probability
    final_risk_entropy = Column(Float, nullable=True)

    total_items = Column(Integer, nullable=True)
    total_time_s = Column(Float, nullable=True)
    final_fatigue_level = Column(Float, nullable=True)

    device_id = Column(String, nullable=True)
    version = Column(String, nullable=True)
    notes = Column(Text, nullable=True)
    session_state = Column(JSON, nullable=True) # JSON snapshot of SessionState
    status = Column(String, nullable=False, default="in_progress") # in_progress, completed
    created_at = Column(DateTime, nullable=True)
    updated_at = Column(DateTime, nullable=True)

    child = relationship("Child", back_populates="tests")
    item_logs = relationship("TestItemLog", back_populates="test")
    module_summaries = relationship("TestModuleSum", back_populates="test")
    features = relationship("TestFeatures", back_populates="test", uselist=False)
    xai_records = relationship("TestXAI", back_populates="test")
