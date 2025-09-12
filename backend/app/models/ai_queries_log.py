from sqlalchemy import Column, Integer, String, Text, TIMESTAMP
from sqlalchemy.sql import func
from app.core.db import Base

class AIQueryLog(Base):
    __tablename__ = "ai_queries_log"

    log_id = Column(Integer, primary_key=True, index=True)
    query_text = Column(Text, nullable=False)
    status = Column(String(20), default="unsupported")
    created_at = Column(TIMESTAMP(timezone=True), server_default=func.now())
