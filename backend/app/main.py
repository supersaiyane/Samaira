from fastapi import FastAPI
from app.routers import accounts, services, budgets, recommendations, anomalies, savings, forecasts

app = FastAPI(
    title="FinOps Toolkit API",
    description="Backend API for FinOps Automation Toolkit",
    version="1.0.0",
)

# Health check
@app.get("/")
async def health_check():
    return {"status": "ok", "message": "FinOps API is running"}

# Register routers
app.include_router(accounts.router, prefix="/api/v1/accounts", tags=["accounts"])
app.include_router(services.router, prefix="/api/v1/services", tags=["services"])
app.include_router(budgets.router, prefix="/api/v1/budgets", tags=["budgets"])
app.include_router(recommendations.router, prefix="/api/v1/recommendations", tags=["recommendations"])
app.include_router(anomalies.router, prefix="/api/v1/anomalies", tags=["anomalies"])
app.include_router(savings.router, prefix="/api/v1/savings", tags=["savings"])
app.include_router(forecasts.router, prefix="/api/v1/forecasts", tags=["forecasts"])
