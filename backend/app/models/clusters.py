from sqlalchemy import Column, Integer, String, TIMESTAMP, ForeignKey, func, Table
from app.core.db import Base

class Cluster(Base):
    __tablename__ = "clusters"

    cluster_id = Column(Integer, primary_key=True, index=True)
    account_id = Column(Integer, ForeignKey("accounts.account_id"))
    cluster_name = Column(String(255))
    cluster_type = Column(String(50))  # EKS, AKS, GKE
    region = Column(String(50))
    created_at = Column(TIMESTAMP(timezone=True), server_default=func.now())

# Junction table for many-to-many (cluster ↔ resources)
from sqlalchemy import Table

ClusterResources = Table(
    "cluster_resources",
    Base.metadata,
    Column("cluster_id", Integer, ForeignKey("clusters.cluster_id"), primary_key=True),
    Column("resource_id", Integer, ForeignKey("resources.resource_id"), primary_key=True),
)
