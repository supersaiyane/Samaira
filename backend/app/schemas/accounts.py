from pydantic import BaseModel
from typing import Optional

# ---------- Base ----------
class AccountBase(BaseModel):
    cloud_provider: str
    account_number: str
    account_name: str
    owner_email: Optional[str] = None

# ---------- Create ----------
class AccountCreate(AccountBase):
    pass

# ---------- Response ----------
class AccountResponse(AccountBase):
    account_id: int

    class Config:
        orm_mode = True
