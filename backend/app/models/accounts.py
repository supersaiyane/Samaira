from sqlalchemy import Column, Integer, String, TIMESTAMP, func
from app.core.db import Base

class Account(Base):
    __tablename__ = "accounts"

    account_id = Column(Integer, primary_key=True, index=True)
    cloud_provider = Column(String(20), nullable=False)   # AWS, Azure, GCP
    account_number = Column(String(100), nullable=False, unique=True)
    account_name = Column(String(255))
    owner_email = Column(String(255))
    created_at = Column(TIMESTAMP(timezone=True), server_default=func.now())
