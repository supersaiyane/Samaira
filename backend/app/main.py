from fastapi import FastAPI
from app.api import v1   # clean import from api/__init__.py

app = FastAPI(title="FinOps Toolkit API", version="1.0.0")

# Health check
@app.get("/")
async def root():
    return {"status": "ok", "service": "FinOps Toolkit API"}

# Register routers with prefixes
app.include_router(v1.accounts.router, prefix="/api/v1/accounts", tags=["Accounts"])
app.include_router(v1.services.router, prefix="/api/v1/services", tags=["Services"])
app.include_router(v1.budgets.router, prefix="/api/v1/budgets", tags=["Budgets"])
app.include_router(v1.recommendations.router, prefix="/api/v1/recommendations", tags=["Recommendations"])
app.include_router(v1.anomalies.router, prefix="/api/v1/anomalies", tags=["Anomalies"])
app.include_router(v1.savings.router, prefix="/api/v1/savings", tags=["Savings"])
app.include_router(v1.forecasts.router, prefix="/api/v1/forecasts", tags=["Forecasts"])
app.include_router(v1.resources.router, prefix="/api/v1/resources", tags=["Resources"])
app.include_router(v1.billing.router, prefix="/api/v1/billing", tags=["Billing"])
app.include_router(v1.usage.router, prefix="/api/v1/usage", tags=["Usage"])
app.include_router(v1.clusters.router, prefix="/api/v1/clusters", tags=["Clusters"])
app.include_router(v1.logs.router, prefix="/api/v1/logs", tags=["Logs"])
app.include_router(v1.service_categories.router, prefix="/api/v1/service-categories", tags=["Service Categories"])
app.include_router(v1.unmapped_services.router, prefix="/api/v1/unmapped-services", tags=["Unmapped Services"])
app.include_router(v1.instance_catalog.router, prefix="/api/v1/instance-catalog", tags=["Instance Catalog"])
