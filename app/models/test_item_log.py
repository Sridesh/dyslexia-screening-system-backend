from sqlalchemy import Column, Integer, String, Boolean, Float, Text, DateTime, ForeignKey
from sqlalchemy.orm import relationship
from app.db.database import Base

class TestItemLog(Base):
    __tablename__ = "test_item_log"

    id = Column(Integer, primary_key=True, index=True)
    test_id = Column(Integer, ForeignKey("test.id"), nullable=False)
    item_id = Column(Integer, ForeignKey("item.id"), nullable=False)

    round_number = Column(Integer, nullable=True)
    within_round_idx = Column(Integer, nullable=True)
    global_index = Column(Integer, nullable=True)

    module = Column(String, index=True, nullable=False)
    difficulty = Column(Float, nullable=True)

    response = Column(Text, nullable=True)
    is_correct = Column(Boolean, nullable=True)
    response_time_s = Column(Float, nullable=True)
    started_at = Column(DateTime, nullable=True)
    submitted_at = Column(DateTime, nullable=True)

    is_switch_question = Column(Boolean, default=False)
    was_slow_correct = Column(Boolean, default=False)
    fatigue_factor_used = Column(Float, nullable=True)

    p_module_weak_before = Column(Float, nullable=True)
    p_module_strong_before = Column(Float, nullable=True)
    p_module_weak_after = Column(Float, nullable=True)
    p_module_strong_after = Column(Float, nullable=True)
    p_risk_atrisk_before = Column(Float, nullable=True)
    p_risk_atrisk_after = Column(Float, nullable=True)

    created_at = Column(DateTime, nullable=True)

    test = relationship("Test", back_populates="item_logs")
    item = relationship("Item", back_populates="logs")
