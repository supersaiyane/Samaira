from sqlalchemy import (
    Column, Integer, String, ForeignKey, Date, Numeric,
    JSON, TIMESTAMP, BigInteger
)
from sqlalchemy.orm import relationship
from app.core.db import Base
from datetime import datetime

# ========================
# Accounts
# ========================
class Account(Base):
    __tablename__ = "accounts"

    account_id = Column(Integer, primary_key=True, index=True)
    cloud_provider = Column(String(20), nullable=False)
    account_number = Column(String(100), unique=True, nullable=False)
    account_name = Column(String(255))
    owner_email = Column(String(255))
    created_at = Column(TIMESTAMP, default=datetime.utcnow)

# ========================
# Service Categories
# ========================
class ServiceCategory(Base):
    __tablename__ = "service_categories"

    category_id = Column(Integer, primary_key=True, index=True)
    category_name = Column(String(100), unique=True, nullable=False)
    description = Column(String)

# ========================
# Services
# ========================
class Service(Base):
    __tablename__ = "services"

    service_id = Column(Integer, primary_key=True, index=True)
    cloud_provider = Column(String(20), nullable=False)
    service_code = Column(String(100), nullable=False)
    service_name = Column(String(255), nullable=False)
    category_id = Column(Integer, ForeignKey("service_categories.category_id"))

# ========================
# Resources
# ========================
class Resource(Base):
    __tablename__ = "resources"

    resource_id = Column(Integer, primary_key=True, index=True)
    account_id = Column(Integer, ForeignKey("accounts.account_id"))
    service_id = Column(Integer, ForeignKey("services.service_id"))
    resource_name = Column(String(255))
    region = Column(String(50))
    resource_type = Column(String(100))
    tags = Column(JSON)
    created_at = Column(TIMESTAMP, default=datetime.utcnow)
    terminated_at = Column(TIMESTAMP)

# ========================
# Billing
# ========================
class Billing(Base):
    __tablename__ = "billing"

    billing_id = Column(BigInteger, primary_key=True, index=True)
    account_id = Column(Integer, ForeignKey("accounts.account_id"))
    service_id = Column(Integer, ForeignKey("services.service_id"))
    resource_id = Column(Integer, ForeignKey("resources.resource_id"))
    usage_date = Column(Date, nullable=False)
    cost_amount = Column(Numeric(18, 6), nullable=False)
    currency = Column(String(10), default="USD")
    usage_type = Column(String(100))
    usage_quantity = Column(Numeric(18, 6))
    pricing_unit = Column(String(50))
    metadata = Column(JSON)
    created_at = Column(TIMESTAMP, default=datetime.utcnow)

# ========================
# Usage
# ========================
class Usage(Base):
    __tablename__ = "usage"

    usage_id = Column(BigInteger, primary_key=True, index=True)
    resource_id = Column(Integer, ForeignKey("resources.resource_id"))
    metric_name = Column(String(100))
    metric_value = Column(Numeric(18, 6))
    unit = Column(String(50))
    collected_at = Column(TIMESTAMP, nullable=False)
    created_at = Column(TIMESTAMP, default=datetime.utcnow)

# ========================
# Clusters
# ========================
class Cluster(Base):
    __tablename__ = "clusters"

    cluster_id = Column(Integer, primary_key=True, index=True)
    account_id = Column(Integer, ForeignKey("accounts.account_id"))
    cluster_name = Column(String(255))
    cluster_type = Column(String(50))  # EKS, AKS, GKE
    region = Column(String(50))
    created_at = Column(TIMESTAMP, default=datetime.utcnow)

class ClusterResource(Base):
    __tablename__ = "cluster_resources"

    cluster_id = Column(Integer, ForeignKey("clusters.cluster_id"), primary_key=True)
    resource_id = Column(Integer, ForeignKey("resources.resource_id"), primary_key=True)

# ========================
# Recommendations
# ========================
class Recommendation(Base):
    __tablename__ = "recommendations"

    rec_id = Column(Integer, primary_key=True, index=True)
    resource_id = Column(Integer, ForeignKey("resources.resource_id"))
    rec_type = Column(String(50))
    current_config = Column(JSON)
    recommended_config = Column(JSON)
    estimated_savings = Column(Numeric(18, 6))
    currency = Column(String(10), default="USD")
    created_at = Column(TIMESTAMP, default=datetime.utcnow)
    status = Column(String(50), default="pending")

# ========================
# Anomalies
# ========================
class Anomaly(Base):
    __tablename__ = "anomalies"

    anomaly_id = Column(Integer, primary_key=True, index=True)
    account_id = Column(Integer, ForeignKey("accounts.account_id"))
    service_id = Column(Integer, ForeignKey("services.service_id"))
    detected_at = Column(TIMESTAMP, default=datetime.utcnow)
    metric = Column(String(100))
    observed_value = Column(Numeric(18, 6))
    expected_value = Column(Numeric(18, 6))
    deviation_percent = Column(Numeric(6, 2))
    details = Column(JSON)

# ========================
# Savings
# ========================
class Saving(Base):
    __tablename__ = "savings"

    saving_id = Column(Integer, primary_key=True, index=True)
    account_id = Column(Integer, ForeignKey("accounts.account_id"))
    resource_id = Column(Integer, ForeignKey("resources.resource_id"))
    rec_id = Column(Integer, ForeignKey("recommendations.rec_id"))
    implemented_at = Column(TIMESTAMP, default=datetime.utcnow)
    actual_savings = Column(Numeric(18, 6))
    currency = Column(String(10), default="USD")

# ========================
# Forecasts
# ========================
class Forecast(Base):
    __tablename__ = "forecasts"

    forecast_id = Column(Integer, primary_key=True, index=True)
    account_id = Column(Integer, ForeignKey("accounts.account_id"))
    service_id = Column(Integer, ForeignKey("services.service_id"))
    generated_at = Column(TIMESTAMP, default=datetime.utcnow)
    forecast_period_start = Column(Date)
    forecast_period_end = Column(Date)
    forecast_amount = Column(Numeric(18, 6))
    currency = Column(String(10), default="USD")
    model_used = Column(String(50))
    confidence_interval = Column(JSON)

# ========================
# Logs
# ========================
class Log(Base):
    __tablename__ = "logs"

    log_id = Column(BigInteger, primary_key=True, index=True)
    timestamp = Column(TIMESTAMP, default=datetime.utcnow)
    level = Column(String(20))
    component = Column(String(100))
    message = Column(String)
    correlation_id = Column(String(36))
    user_id = Column(String(255))
    extra = Column(JSON)

# ========================
# Unmapped Services
# ========================
class UnmappedService(Base):
    __tablename__ = "unmapped_services"

    id = Column(Integer, primary_key=True, index=True)
    cloud_provider = Column(String(20), nullable=False)
    service_name = Column(String(255), nullable=False)
    first_seen = Column(TIMESTAMP, default=datetime.utcnow)
    last_seen = Column(TIMESTAMP, default=datetime.utcnow)


# ========================
# Instance Catalog
# ========================
class InstanceCatalog(Base):
    __tablename__ = "instance_catalog"

    id = Column(Integer, primary_key=True, index=True)
    family = Column(String(50), nullable=False)
    size = Column(String(50), nullable=False)
    vcpu = Column(Integer)
    memory_gb = Column(Numeric(10, 2))
    region = Column(String(50))
    price_per_hour = Column(Numeric(10, 4))
    last_updated = Column(TIMESTAMP, default=datetime.utcnow)

# ========================
# Budgets
# ========================
class Budget(Base):
    __tablename__ = "budgets"

    budget_id = Column(Integer, primary_key=True, index=True)
    budget_name = Column(String(100), nullable=False)
    account_id = Column(Integer, ForeignKey("accounts.account_id"), nullable=True)
    service_id = Column(Integer, ForeignKey("services.service_id"), nullable=True)
    budget_limit = Column(Numeric(18, 6), nullable=False)
    currency = Column(String(10), default="USD")
    created_at = Column(TIMESTAMP, default=datetime.utcnow)

# ========================
# Insights
# ========================
class Insight(Base):
    __tablename__ = "insights"

    insight_id = Column(Integer, primary_key=True, index=True)
    account_id = Column(Integer, ForeignKey("accounts.account_id"), nullable=True)
    service_id = Column(Integer, ForeignKey("services.service_id"), nullable=True)
    insight_type = Column(String(50))   # trend, savings, idle, forecast_gap
    severity = Column(String(20))       # info, warning, critical
    message = Column(String)
    metadata = Column(JSON)
    created_at = Column(TIMESTAMP, default=datetime.utcnow)

# ========================
# AI Query Log
# ========================
class AIQueryLog(Base):
    __tablename__ = "ai_queries_log"

    log_id = Column(Integer, primary_key=True, index=True)
    query_text = Column(Text, nullable=False)
    status = Column(String(20), default="unsupported")  # supported, unsupported
    created_at = Column(TIMESTAMP, default=datetime.utcnow)