from pydantic import BaseModel
from datetime import datetime

class AIQueryLogBase(BaseModel):
    query_text: str
    status: str = "unsupported"

class AIQueryLogResponse(AIQueryLogBase):
    log_id: int
    created_at: datetime

    class Config:
        orm_mode = True
