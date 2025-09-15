from pydantic import BaseModel
from datetime import datetime
from typing import Optional

class AIQueryLogBase(BaseModel):
    query_text: str
    status: str = "unsupported"
    sql_generated: Optional[str] = None

class AIQueryLogResponse(AIQueryLogBase):
    id: int                           
    created_at: datetime

    class Config:
        orm_mode = True