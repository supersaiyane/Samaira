from pydantic import BaseModel
from typing import Optional
from datetime import datetime

# ---------- Base ----------
class SavingBase(BaseModel):
    account_id: Optional[int] = None
    resource_id: Optional[int] = None
    rec_id: Optional[int] = None
    actual_savings: float
    currency: str = "USD"

# ---------- Response ----------
class SavingResponse(SavingBase):
    saving_id: int
    implemented_at: datetime

    class Config:
        orm_mode = True

# ---------- Summary ----------
class SavingSummary(BaseModel):
    total_savings: float
    currency: str
