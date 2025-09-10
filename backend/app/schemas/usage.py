from pydantic import BaseModel
from typing import Optional
from datetime import datetime

# ---------- Base ----------
class UsageBase(BaseModel):
    resource_id: int
    metric_name: str
    metric_value: float
    unit: Optional[str] = None
    collected_at: datetime

# ---------- Response ----------
class UsageResponse(UsageBase):
    usage_id: int
    created_at: datetime

    class Config:
        orm_mode = True
