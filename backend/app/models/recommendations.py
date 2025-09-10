from sqlalchemy import Column, Integer, String, Numeric, TIMESTAMP, ForeignKey, func
from sqlalchemy.dialects.postgresql import JSONB
from app.core.db import Base

class Recommendation(Base):
    __tablename__ = "recommendations"

    rec_id = Column(Integer, primary_key=True, index=True)
    resource_id = Column(Integer, ForeignKey("resources.resource_id"))
    rec_type = Column(String(50))  # Rightsize, Idle, RI, SP
    current_config = Column(JSONB)
    recommended_config = Column(JSONB)
    estimated_savings = Column(Numeric(18,6))
    currency = Column(String(10), default="USD")
    created_at = Column(TIMESTAMP(timezone=True), server_default=func.now())
    status = Column(String(50), default="pending")
