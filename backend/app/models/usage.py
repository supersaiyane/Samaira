from sqlalchemy import Column, Integer, BigInteger, String, Numeric, TIMESTAMP, ForeignKey, func
from app.core.db import Base

class Usage(Base):
    __tablename__ = "usage"

    usage_id = Column(BigInteger, primary_key=True, index=True)
    resource_id = Column(Integer, ForeignKey("resources.resource_id"))
    metric_name = Column(String(100))
    metric_value = Column(Numeric(18,6))
    unit = Column(String(50))
    collected_at = Column(TIMESTAMP(timezone=True), nullable=False)
    created_at = Column(TIMESTAMP(timezone=True), server_default=func.now())
