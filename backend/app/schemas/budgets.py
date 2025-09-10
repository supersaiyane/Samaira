from pydantic import BaseModel
from typing import Optional
from datetime import date

# ---------- Base ----------
class BudgetBase(BaseModel):
    account_id: Optional[int] = None
    service_id: Optional[int] = None
    budget_name: str
    budget_limit: float
    currency: str = "USD"
    period: str = "monthly"  # monthly, quarterly, yearly
    start_date: Optional[date] = None
    end_date: Optional[date] = None

# ---------- Create ----------
class BudgetCreate(BudgetBase):
    pass

# ---------- Response ----------
class BudgetResponse(BudgetBase):
    budget_id: int

    class Config:
        orm_mode = True
