from sqlalchemy import Column, Integer, String, TIMESTAMP, ForeignKey, func
from sqlalchemy.dialects.postgresql import JSONB
from app.core.db import Base

class Resource(Base):
    __tablename__ = "resources"

    resource_id = Column(Integer, primary_key=True, index=True)
    account_id = Column(Integer, ForeignKey("accounts.account_id"))
    service_id = Column(Integer, ForeignKey("services.service_id"))
    resource_name = Column(String(255))
    region = Column(String(50))
    resource_type = Column(String(100))
    tags = Column(JSONB)
    created_at = Column(TIMESTAMP(timezone=True), server_default=func.now())
    terminated_at = Column(TIMESTAMP(timezone=True))
