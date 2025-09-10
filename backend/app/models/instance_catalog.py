from sqlalchemy import Column, String, Integer, Numeric, Boolean, TIMESTAMP
from app.core.db import Base
from datetime import datetime

class InstanceCatalog(Base):
    __tablename__ = "instance_catalog"

    instance_type = Column(String(50), primary_key=True, index=True)  # e.g. m5.xlarge
    family = Column(String(20), nullable=False)                       # e.g. m5
    size = Column(String(20), nullable=False)                         # e.g. xlarge
    vcpu = Column(Integer)
    memory_gb = Column(Numeric)
    storage = Column(String)
    network_performance = Column(String)
    generation = Column(String)                                       # x86_64, arm64, etc.
    baremetal = Column(Boolean, default=False)
    gpu_count = Column(Integer, default=0)
    last_updated = Column(TIMESTAMP, default=datetime.utcnow)
