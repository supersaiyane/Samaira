from sqlalchemy import Column, Integer, String, ForeignKey, TIMESTAMP, Text, JSON
from sqlalchemy.sql import func
from app.core.db import Base

class Insight(Base):
    __tablename__ = "insights"

    insight_id = Column(Integer, primary_key=True, index=True)
    account_id = Column(Integer, ForeignKey("accounts.account_id"), nullable=True)
    service_id = Column(Integer, ForeignKey("services.service_id"), nullable=True)
    insight_type = Column(String(50), nullable=False)      # trend, savings, idle, forecast_gap
    severity = Column(String(20), nullable=False, default="info")  # info, warning, critical
    message = Column(Text, nullable=False)
    metadata = Column(JSON, nullable=True)
    created_at = Column(TIMESTAMP(timezone=True), server_default=func.now())
