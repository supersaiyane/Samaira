from sqlalchemy import Column, BigInteger, String, TIMESTAMP, Text, UUID
from sqlalchemy.dialects.postgresql import JSONB
from app.core.db import Base
from sqlalchemy.sql import func

class Log(Base):
    __tablename__ = "logs"

    log_id = Column(BigInteger, primary_key=True, index=True)
    timestamp = Column(TIMESTAMP(timezone=True), server_default=func.now())
    level = Column(String(20))         # INFO, WARN, ERROR
    component = Column(String(100))    # backend, airflow, ingestion
    message = Column(Text)
    correlation_id = Column(UUID, nullable=True)
    user_id = Column(String(255), nullable=True)
    extra = Column(JSONB)
