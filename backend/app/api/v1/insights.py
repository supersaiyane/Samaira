from fastapi import APIRouter, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession
from app.core.db import get_db
from app.schemas.insights import InsightResponse, InsightSummary
from app.services import insights_service

router = APIRouter()

@router.get("/", response_model=list[InsightResponse])
async def list_insights(db: AsyncSession = Depends(get_db)):
    return await insights_service.list_insights(db)

@router.get("/{insight_id}", response_model=InsightResponse)
async def get_insight(insight_id: int, db: AsyncSession = Depends(get_db)):
    insight = await insights_service.get_insight(db, insight_id)
    if not insight:
        raise HTTPException(status_code=404, detail="Insight not found")
    return insight

@router.get("/summary", response_model=InsightSummary)
async def insights_summary(
    days: int = Query(30, description="Lookback window in days"),
    account_id: int | None = Query(None, description="Filter by account ID"),
    service_id: int | None = Query(None, description="Filter by service ID"),
    severity: str | None = Query(None, description="Filter by severity"),
    insight_type: str | None = Query(None, description="Filter by insight type"),
    db: AsyncSession = Depends(get_db),
):
    """
    Aggregated summary for FinOps Overview Dashboard.
    Returns:
    - total_cost_mtd
    - total_savings
    - active_anomalies
    - forecast_30d
    - daily_trend
    """
    summary = await insights_service.insights_summary(
        db, days, account_id, service_id, severity, insight_type
    )

    # Ensure shape for frontend
    return {
        "total_cost_mtd": float(summary.get("total_cost_mtd", 0)),
        "total_savings": float(summary.get("total_savings", 0)),
        "active_anomalies": int(summary.get("active_anomalies", 0)),
        "forecast_30d": float(summary.get("forecast_30d", 0)),
        "daily_trend": summary.get("daily_trend", []),
    }