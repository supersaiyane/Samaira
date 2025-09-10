from sqlalchemy import Column, Integer, String
from app.core.db import Base

class ServiceCategory(Base):
    __tablename__ = "service_categories"

    category_id = Column(Integer, primary_key=True, index=True)
    category_name = Column(String(100), unique=True, nullable=False)
    description = Column(String)
