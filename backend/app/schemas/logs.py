from pydantic import BaseModel
from typing import Optional, Dict, Any
from datetime import datetime

# ---------- Base ----------
class LogBase(BaseModel):
    level: str                 # INFO, WARN, ERROR
    component: str             # backend, airflow, ingestion, ai_engine
    message: str
    correlation_id: Optional[str] = None
    user_id: Optional[str] = None
    extra: Optional[Dict[str, Any]] = None

# ---------- Response ----------
class LogResponse(LogBase):
    log_id: int
    timestamp: datetime

    class Config:
        orm_mode = True
