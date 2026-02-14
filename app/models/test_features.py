from sqlalchemy import Column, Integer, Float, DateTime, ForeignKey
from sqlalchemy.orm import relationship
from app.db.database import Base

class TestFeatures(Base):
    __tablename__ = "test_features"

    test_id = Column(Integer, ForeignKey("test.id"), primary_key=True, index=True)

    # Overall features
    p_risk_atrisk = Column(Float, nullable=True)
    risk_entropy = Column(Float, nullable=True)
    total_items = Column(Integer, nullable=True)
    total_time_s = Column(Float, nullable=True)
    final_fatigue = Column(Float, nullable=True)

    # Per-module flattened features (examples for RAN & phonology; extend as needed)
    p_weak_RAN = Column(Float, nullable=True)
    entropy_RAN = Column(Float, nullable=True)
    num_items_RAN = Column(Integer, nullable=True)
    avg_time_RAN = Column(Float, nullable=True)
    slow_corr_ratio_RAN = Column(Float, nullable=True)
    avg_switch_rt_RAN = Column(Float, nullable=True)

    p_weak_phonology = Column(Float, nullable=True)
    entropy_phonology = Column(Float, nullable=True)
    num_items_phonology = Column(Integer, nullable=True)
    avg_time_phonology = Column(Float, nullable=True)
    slow_corr_ratio_phonology = Column(Float, nullable=True)
    avg_switch_rt_phonology = Column(Float, nullable=True)

    # add more modules here...

    created_at = Column(DateTime, nullable=True)

    test = relationship("Test", back_populates="features")
