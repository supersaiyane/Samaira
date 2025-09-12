from pydantic import BaseModel
from typing import Any, Optional

class AIQueryRequest(BaseModel):
    query: str

class AIQueryResponse(BaseModel):
    query: str
    sql: str
    result: Any
    summary: str
