from sqlalchemy import Column, Integer, String, Numeric, Date, TIMESTAMP, ForeignKey, func
from sqlalchemy.dialects.postgresql import JSONB
from app.core.db import Base

class Forecast(Base):
    __tablename__ = "forecasts"

    forecast_id = Column(Integer, primary_key=True, index=True)
    account_id = Column(Integer, ForeignKey("accounts.account_id"))
    service_id = Column(Integer, ForeignKey("services.service_id"))
    generated_at = Column(TIMESTAMP(timezone=True), server_default=func.now())
    forecast_period_start = Column(Date)
    forecast_period_end = Column(Date)
    forecast_amount = Column(Numeric(18,6))
    currency = Column(String(10), default="USD")
    model_used = Column(String(50))
    confidence_interval = Column(JSONB)
