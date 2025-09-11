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
    Returns aggregated counts by severity, top services, daily trend, and top accounts.
    Optional filters: account_id, service_id, severity, insight_type.
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

    # --- Severity counts ---
    query = text(f"""
        SELECT severity, COUNT(*) AS count
        FROM insights
        WHERE {where_clause}
        GROUP BY severity
    """)
    severity_counts = (await db.execute(query, params)).mappings().all()

    # --- Top services ---
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

    # --- Daily trend ---
    query3 = text(f"""
        SELECT DATE(created_at) AS day, COUNT(*) AS count
        FROM insights
        WHERE {where_clause}
        GROUP BY day
        ORDER BY day ASC
    """)
    trend = (await db.execute(query3, params)).mappings().all()

    # --- Top accounts ---
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

    return {
        "by_severity": severity_counts,
        "top_services": top_services,
        "trend": trend,
        "top_accounts": top_accounts,
    }
