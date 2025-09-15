from sqlalchemy import Column, Integer, String, Text, DateTime
from sqlalchemy.sql import func
from app.db.base_class import Base  # assuming you have Base defined here

class AIQueryLog(Base):
    __tablename__ = "ai_queries_log"

    id = Column(Integer, primary_key=True, index=True)
    query_text = Column(Text, nullable=False)          # original NL query
    sql_generated = Column(Text, nullable=True)        # SQL used/generated
    status = Column(String(50), nullable=False)        # yaml | llm | unsafe | unsupported
    created_at = Column(DateTime(timezone=True), server_default=func.now())