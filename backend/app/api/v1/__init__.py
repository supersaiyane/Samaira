from fastapi import APIRouter
from . import accounts, savings, insights, ai, metrics  # ✅ added metrics

api_router = APIRouter()
api_router.include_router(accounts.router, prefix="/accounts", tags=["accounts"])
api_router.include_router(savings.router, prefix="/savings", tags=["savings"])
api_router.include_router(insights.router, prefix="/insights", tags=["insights"])
api_router.include_router(ai.router, prefix="/ai", tags=["ai"])
api_router.include_router(metrics.router, prefix="/metrics", tags=["metrics"])  # ✅ new
