from app.models.accounts import Account
from app.models.service_categories import ServiceCategory
from app.models.services import Service
from app.models.resources import Resource
from app.models.billing import Billing
from app.models.usage import Usage
from app.models.clusters import Cluster, ClusterResource
from app.models.recommendations import Recommendation
from app.models.anomalies import Anomaly
from app.models.savings import Saving
from app.models.forecasts import Forecast
from app.models.logs import Log
from app.models.unmapped_services import UnmappedService
from app.models.instance_catalog import InstanceCatalog
from app.models.budgets import Budget

# This makes Alembic autogenerate migrations correctly
ALL_MODELS = [
    Account,
    ServiceCategory,
    Service,
    Resource,
    Billing,
    Usage,
    Cluster,
    ClusterResource,
    Recommendation,
    Anomaly,
    Saving,
    Forecast,
    Log,
    UnmappedService,
    InstanceCatalog,
    Budget,
]
