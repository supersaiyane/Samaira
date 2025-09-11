from pydantic import BaseModel
from datetime import datetime, date
from typing import Optional

class SavingBase(BaseModel):
    account_id: Optional[int]
    resource_id: Optional[int]
    rec_id: Optional[int]
    actual_savings: float
    currency: str = "USD"
    implemented_at: Optional[datetime]

class SavingResponse(SavingBase):
    saving_id: int

    class Config:
        orm_mode = True

class SavingSummary(BaseModel):
    total_savings: float
    currency: str = "USD"

class SavingSummaryBreakdown(BaseModel):
    month: date
    account_name: str
    service_name: str
    total_savings: float

    class Config:
        orm_mode = True
