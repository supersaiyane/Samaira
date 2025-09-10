from sqlalchemy import Column, Integer, String, Numeric, TIMESTAMP, ForeignKey, func
from sqlalchemy.dialects.postgresql import JSONB
from app.core.db import Base

class Anomaly(Base):
    __tablename__ = "anomalies"

    anomaly_id = Column(Integer, primary_key=True, index=True)
    account_id = Column(Integer, ForeignKey("accounts.account_id"))
    service_id = Column(Integer, ForeignKey("services.service_id"))
    detected_at = Column(TIMESTAMP(timezone=True), server_default=func.now())
    metric = Column(String(100))   # cost, usage
    observed_value = Column(Numeric(18,6))
    expected_value = Column(Numeric(18,6))
    deviation_percent = Column(Numeric(6,2))
    details = Column(JSONB)
