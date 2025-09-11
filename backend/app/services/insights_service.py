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

async def insights_summary(db: AsyncSession, days: int = 30):
    """
    Returns aggregated counts by severity, top services, and daily trend.
    """
    # --- Severity counts ---
    query = text("""
        SELECT 
            severity,
            COUNT(*) AS count
        FROM insights
        WHERE created_at >= NOW() - INTERVAL :days || ' day'
        GROUP BY severity
    """)
    severity_counts = (await db.execute(query, {"days": days})).mappings().all()

    # --- Top services ---
    query2 = text("""
        SELECT s.service_name, COUNT(*) AS count
        FROM insights i
        JOIN services s ON i.service_id = s.service_id
        WHERE i.created_at >= NOW() - INTERVAL :days || ' day'
        GROUP BY s.service_name
        ORDER BY count DESC
        LIMIT 5
    """)
    top_services = (await db.execute(query2, {"days": days})).mappings().all()

    # --- Daily trend ---
    query3 = text("""
        SELECT 
            DATE(created_at) AS day,
            COUNT(*) AS count
        FROM insights
        WHERE created_at >= NOW() - INTERVAL :days || ' day'
        GROUP BY day
        ORDER BY day ASC
    """)
    trend = (await db.execute(query3, {"days": days})).mappings().all()

    return {
        "by_severity": severity_counts,
        "top_services": top_services,
        "trend": trend,
    }
