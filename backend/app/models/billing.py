from sqlalchemy import Column, Integer, BigInteger, Date, Numeric, String, ForeignKey, TIMESTAMP, func
from sqlalchemy.dialects.postgresql import JSONB
from app.core.db import Base

class Billing(Base):
    __tablename__ = "billing"

    billing_id = Column(BigInteger, primary_key=True, index=True)
    account_id = Column(Integer, ForeignKey("accounts.account_id"))
    service_id = Column(Integer, ForeignKey("services.service_id"))
    resource_id = Column(Integer, ForeignKey("resources.resource_id"))
    usage_date = Column(Date, nullable=False)
    cost_amount = Column(Numeric(18,6), nullable=False)
    currency = Column(String(10), default="USD")
    usage_type = Column(String(100))
    usage_quantity = Column(Numeric(18,6))
    pricing_unit = Column(String(50))
    metadata = Column(JSONB)
    created_at = Column(TIMESTAMP(timezone=True), server_default=func.now())
