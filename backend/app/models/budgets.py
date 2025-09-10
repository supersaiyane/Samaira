from sqlalchemy import Column, Integer, String, Numeric, Date, TIMESTAMP, ForeignKey
from sqlalchemy.sql import func
from app.core.db import Base

class Budget(Base):
    __tablename__ = "budgets"

    budget_id = Column(Integer, primary_key=True, index=True)
    account_id = Column(Integer, ForeignKey("accounts.account_id", ondelete="CASCADE"), nullable=True)
    service_id = Column(Integer, ForeignKey("services.service_id", ondelete="CASCADE"), nullable=True)

    budget_name = Column(String(255), nullable=False)
    budget_limit = Column(Numeric(18, 6), nullable=False)
    currency = Column(String(10), default="USD")
    period = Column(String(20), default="monthly")  # monthly, quarterly, yearly
    start_date = Column(Date, default=func.current_date())
    end_date = Column(Date, nullable=True)

    created_at = Column(TIMESTAMP(timezone=True), server_default=func.now())
    updated_at = Column(TIMESTAMP(timezone=True), server_default=func.now(), onupdate=func.now())
