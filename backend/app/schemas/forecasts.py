from pydantic import BaseModel
from typing import Optional, Dict, Any
from datetime import datetime, date

# ---------- Base ----------
class ForecastBase(BaseModel):
    account_id: Optional[int] = None
    service_id: Optional[int] = None
    forecast_period_start: Optional[date] = None
    forecast_period_end: Optional[date] = None
    forecast_amount: float
    currency: str = "USD"
    model_used: str
    confidence_interval: Optional[Dict[str, Any]] = None

# ---------- Response ----------
class ForecastResponse(ForecastBase):
    forecast_id: int
    generated_at: datetime

    class Config:
        orm_mode = True
