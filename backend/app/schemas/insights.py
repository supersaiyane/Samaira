from pydantic import BaseModel
from datetime import datetime
from typing import Optional, Any, List

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

class SeverityCount(BaseModel):
    severity: str
    count: int

class ServiceCount(BaseModel):
    service_name: str
    count: int

class TrendPoint(BaseModel):
    day: str
    count: int

class AccountCount(BaseModel):
    account_name: str
    count: int

class DailyTrend(BaseModel):
    date: str
    cost: float


class InsightSummary(BaseModel):
    by_severity: List[SeverityCount]
    top_services: List[ServiceCount]
    trend : List[TrendPoint]
    top_accounts: List[AccountCount]    
    total_cost_mtd: float
    total_savings: float
    active_anomalies: int
    forecast_30d: float
    daily_trend: List[DailyTrend]

