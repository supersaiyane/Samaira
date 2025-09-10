from pydantic import BaseModel
from typing import Optional, List
from datetime import datetime
from app.schemas.resources import ResourceResponse

# ---------- Base ----------
class ClusterBase(BaseModel):
    account_id: Optional[int] = None
    cluster_name: str
    cluster_type: str       # EKS, ECS, AKS, GKE
    region: Optional[str] = None

# ---------- Create ----------
class ClusterCreate(ClusterBase):
    pass

# ---------- Response ----------
class ClusterResponse(ClusterBase):
    cluster_id: int
    created_at: datetime

    class Config:
        orm_mode = True

# ---------- Cluster with Resources ----------
class ClusterWithResources(BaseModel):
    cluster: ClusterResponse
    resources: List[ResourceResponse]
