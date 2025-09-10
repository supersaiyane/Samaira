from pydantic import BaseModel
from typing import Optional, Dict, Any
from datetime import datetime, date

# ---------- Base ----------
class BillingBase(BaseModel):
    account_id: Optional[int] = None
    service_id: Optional[int] = None
    resource_id: Optional[int] = None
    usage_date: date
    cost_amount: float
    currency: str = "USD"
    usage_type: Optional[str] = None
    usage_quantity: Optional[float] = None
    pricing_unit: Optional[str] = None
    metadata: Optional[Dict[str, Any]] = None

# ---------- Response ----------
class BillingResponse(BillingBase):
    billing_id: int
    created_at: datetime

    class Config:
        orm_mode = True
