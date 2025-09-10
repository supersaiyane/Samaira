from pydantic import BaseModel
from typing import Optional, Dict, Any
from datetime import datetime

# ---------- Base ----------
class AnomalyBase(BaseModel):
    account_id: Optional[int] = None
    service_id: Optional[int] = None
    metric: str                # cost, usage, etc.
    observed_value: float
    expected_value: Optional[float] = None
    deviation_percent: Optional[float] = None
    details: Optional[Dict[str, Any]] = None

# ---------- Update ----------
class AnomalyUpdate(BaseModel):
    status: Optional[str] = None   # unresolved, remediated, ignored

# ---------- Response ----------
class AnomalyResponse(AnomalyBase):
    anomaly_id: int
    detected_at: datetime
    status: Optional[str] = None

    class Config:
        orm_mode = True
