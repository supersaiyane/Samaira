from sqlalchemy import Column, Integer, String, TIMESTAMP
from datetime import datetime
from app.core.db import Base

class UnmappedService(Base):
    __tablename__ = "unmapped_services"

    id = Column(Integer, primary_key=True, index=True)
    cloud_provider = Column(String(20), nullable=False)
    service_name = Column(String(255), nullable=False)
    first_seen = Column(TIMESTAMP, default=datetime.utcnow)
    last_seen = Column(TIMESTAMP, default=datetime.utcnow)
