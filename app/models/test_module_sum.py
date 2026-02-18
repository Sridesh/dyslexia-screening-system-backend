from sqlalchemy import Column, Integer, String, Float, DateTime, ForeignKey
from sqlalchemy.orm import relationship
from app.db.database import Base

class TestModuleSum(Base):
    __tablename__ = "test_module_sum"

    id = Column(Integer, primary_key=True, index=True)
    test_id = Column(Integer, ForeignKey("test.id"), nullable=False)
    module = Column(String, index=True, nullable=False)
    risk_label = Column(String, nullable=True) # weak, strong, uncertain

    p_weak_final = Column(Float, nullable=True)
    p_strong_final = Column(Float, nullable=True)
    entropy_final = Column(Float, nullable=True)

    num_items = Column(Integer, nullable=True)
    avg_time_s = Column(Float, nullable=True)
    min_time_s = Column(Float, nullable=True)
    max_time_s = Column(Float, nullable=True)

    slow_correct_count = Column(Integer, nullable=True)
    total_correct_count = Column(Integer, nullable=True)
    slow_correct_ratio = Column(Float, nullable=True)

    avg_switch_rt_s = Column(Float, nullable=True)
    switch_count = Column(Integer, nullable=True)

    first_round_seen = Column(Integer, nullable=True)
    last_round_seen = Column(Integer, nullable=True)

    created_at = Column(DateTime, nullable=True)

    test = relationship("Test", back_populates="module_summaries")
