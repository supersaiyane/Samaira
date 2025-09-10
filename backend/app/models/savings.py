from sqlalchemy import Column, Integer, Numeric, TIMESTAMP, ForeignKey, func
from app.core.db import Base

class Saving(Base):
    __tablename__ = "savings"

    saving_id = Column(Integer, primary_key=True, index=True)
    account_id = Column(Integer, ForeignKey("accounts.account_id"))
    resource_id = Column(Integer, ForeignKey("resources.resource_id"))
    rec_id = Column(Integer, ForeignKey("recommendations.rec_id"))
    implemented_at = Column(TIMESTAMP(timezone=True), server_default=func.now())
    actual_savings = Column(Numeric(18,6))
    currency = Column(String(10), default="USD")
