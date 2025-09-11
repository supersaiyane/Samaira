from pydantic import BaseModel
from datetime import datetime
from typing import Optional, Any

class InsightBase(BaseModel):
    account_id: Optional[int]
    service_id: Optional[int]
    insight_type: str
    severity: str
    message: str
    metadata: Optional[Any]

class InsightResponse(InsightBase):
    insight_id: int
    created_at: datetime

    class Config:
        orm_mode = True
