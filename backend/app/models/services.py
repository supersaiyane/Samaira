from sqlalchemy import Column, Integer, String, ForeignKey
from app.core.db import Base

class Service(Base):
    __tablename__ = "services"

    service_id = Column(Integer, primary_key=True, index=True)
    cloud_provider = Column(String(20), nullable=False)
    service_code = Column(String(100), nullable=False)
    service_name = Column(String(255), nullable=False)
    category_id = Column(Integer, ForeignKey("service_categories.category_id"))