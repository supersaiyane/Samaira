from pydantic import BaseModel
from typing import Optional
from datetime import datetime

class InstanceCatalogResponse(BaseModel):
    instance_type: str
    family: str
    vcpu: int
    memory_gb: float
    price_usd: Optional[float] = None
    last_updated: datetime

    class Config:
        orm_mode = True
