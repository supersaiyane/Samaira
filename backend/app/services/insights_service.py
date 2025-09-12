from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import text
from sqlalchemy.future import select
from app.models.insights import Insight

async def list_insights(db: AsyncSession):
    result = await db.execute(select(Insight).order_by(Insight.created_at.desc()))
    return result.scalars().all()

async def get_insight(db: AsyncSession, insight_id: int):
    result = await db.execute(select(Insight).where(Insight.insight_id == insight_id))
    return result.scalars().first()

async def insights_summary(
    db: AsyncSession,
    days: int = 30,
    account_id: int | None = None,
    service_id: int | None = None,
    severity: str | None = None,
    insight_type: str | None = None,
):
    """
    Returns:
    - Existing insights analytics: by_severity, top_services, trend, top_accounts
    - New FinOps KPIs: total_cost_mtd, total_savings, active_anomalies, forecast_30d, daily_trend
    """

    filters = ["created_at >= NOW() - INTERVAL :days || ' day'"]
    params = {"days": days}

    if account_id:
        filters.append("account_id = :account_id")
        params["account_id"] = account_id
    if service_id:
        filters.append("service_id = :service_id")
        params["service_id"] = service_id
    if severity:
        filters.append("severity = :severity")
        params["severity"] = severity.lower()
    if insight_type:
        filters.append("insight_type = :insight_type")
        params["insight_type"] = insight_type.lower()

    where_clause = " AND ".join(filters)

    # --- Existing: Severity counts ---
    query = text(f"""
        SELECT severity, COUNT(*) AS count
        FROM insights
        WHERE {where_clause}
        GROUP BY severity
    """)
    severity_counts = (await db.execute(query, params)).mappings().all()

    # --- Existing: Top services ---
    query2 = text(f"""
        SELECT s.service_name, COUNT(*) AS count
        FROM insights i
        JOIN services s ON i.service_id = s.service_id
        WHERE {where_clause}
        GROUP BY s.service_name
        ORDER BY count DESC
        LIMIT 5
    """)
    top_services = (await db.execute(query2, params)).mappings().all()

    # --- Existing: Daily trend (insight counts) ---
    query3 = text(f"""
        SELECT DATE(created_at) AS day, COUNT(*) AS count
        FROM insights
        WHERE {where_clause}
        GROUP BY day
        ORDER BY day ASC
    """)
    trend = (await db.execute(query3, params)).mappings().all()

    # --- Existing: Top accounts ---
    query4 = text(f"""
        SELECT a.account_name, COUNT(*) AS count
        FROM insights i
        JOIN accounts a ON i.account_id = a.account_id
        WHERE {where_clause}
        GROUP BY a.account_name
        ORDER BY count DESC
        LIMIT 5
    """)
    top_accounts = (await db.execute(query4, params)).mappings().all()

    # =====================================================
    # New Additions for Overview Dashboard
    # =====================================================

    # --- Total Cost MTD ---
    query_cost = text("""
        SELECT COALESCE(SUM(cost_amount), 0)
        FROM billing
        WHERE date_trunc('month', usage_date) = date_trunc('month', CURRENT_DATE)
    """)
    total_cost_mtd = (await db.execute(query_cost)).scalar() or 0

    # --- Total Savings ---
    query_savings = text("SELECT COALESCE(SUM(actual_savings), 0) FROM savings")
    total_savings = (await db.execute(query_savings)).scalar() or 0

    # --- Active Anomalies ---
    query_anomalies = text("""
        SELECT COUNT(*) FROM anomalies
        WHERE details->>'status' IS NULL OR details->>'status' = 'unresolved'
    """)
    active_anomalies = (await db.execute(query_anomalies)).scalar() or 0

    # --- Forecast (30 days horizon) ---
    query_forecast = text("""
        SELECT COALESCE(AVG(forecast_amount), 0)
        FROM forecasts
        WHERE forecast_period_end >= CURRENT_DATE + INTERVAL '30 days'
    """)
    forecast_30d = (await db.execute(query_forecast)).scalar() or 0

    # --- Daily Cost Trend (last N days) ---
    query_trend_cost = text(f"""
        SELECT usage_date, SUM(cost_amount) AS cost
        FROM billing
        WHERE usage_date >= CURRENT_DATE - INTERVAL :days || ' day'
        GROUP BY usage_date
        ORDER BY usage_date
    """)
    rows = (await db.execute(query_trend_cost, {"days": days})).fetchall()
    daily_trend = [{"date": r[0].strftime("%Y-%m-%d"), "cost": float(r[1])} for r in rows]

    # =====================================================
    # Merge Results
    # =====================================================
    return {
        "by_severity": severity_counts,
        "top_services": top_services,
        "trend": trend,
        "top_accounts": top_accounts,
        "total_cost_mtd": float(total_cost_mtd),
        "total_savings": float(total_savings),
        "active_anomalies": int(active_anomalies),
        "forecast_30d": float(forecast_30d),
        "daily_trend": daily_trend,
    }
