from pydantic import BaseModel
from typing import Optional

class UnmappedServiceResponse(BaseModel):
    service_id: int
    raw_name: str
    cloud_provider: Optional[str] = None

    class Config:
        orm_mode = True
