from pydantic import BaseModel
from typing import Optional, Dict, Any
from datetime import datetime

# ---------- Base ----------
class ResourceBase(BaseModel):
    account_id: Optional[int] = None
    service_id: Optional[int] = None
    resource_name: Optional[str] = None
    region: Optional[str] = None
    resource_type: Optional[str] = None
    tags: Optional[Dict[str, Any]] = None

# ---------- Create ----------
class ResourceCreate(ResourceBase):
    pass

# ---------- Response ----------
class ResourceResponse(ResourceBase):
    resource_id: int
    created_at: datetime
    terminated_at: Optional[datetime] = None

    class Config:
        orm_mode = True
