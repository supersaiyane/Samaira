from pydantic import BaseModel
from typing import Optional

# ---------- Base ----------
class ServiceBase(BaseModel):
    cloud_provider: str
    service_code: str
    service_name: str
    category: Optional[str] = None

# ---------- Create ----------
class ServiceCreate(ServiceBase):
    pass

# ---------- Response ----------
class ServiceResponse(ServiceBase):
    service_id: int

    class Config:
        orm_mode = True
