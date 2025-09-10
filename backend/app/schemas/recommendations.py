from pydantic import BaseModel
from typing import Optional, Dict, Any

# ---------- Base ----------
class RecommendationBase(BaseModel):
    resource_id: int
    rec_type: str                    # Rightsize, Idle, ReservedInstance, SavingsPlan
    current_config: Dict[str, Any]
    recommended_config: Optional[Dict[str, Any]] = None
    estimated_savings: Optional[float] = 0.0
    currency: str = "USD"
    status: str = "pending"          # pending, applied, validated, dismissed, no_savings

# ---------- Create ----------
class RecommendationCreate(RecommendationBase):
    pass

# ---------- Update ----------
class RecommendationUpdate(BaseModel):
    status: Optional[str] = None
    recommended_config: Optional[Dict[str, Any]] = None

# ---------- Response ----------
class RecommendationResponse(RecommendationBase):
    rec_id: int

    class Config:
        orm_mode = True
