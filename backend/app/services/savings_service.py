from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import text
from sqlalchemy.future import select, func
from app.models.savings import Saving

async def list_savings(db: AsyncSession):
    result = await db.execute(select(Saving))
    return result.scalars().all()

async def get_saving(db: AsyncSession, saving_id: int):
    result = await db.execute(select(Saving).where(Saving.saving_id == saving_id))
    return result.scalars().first()

async def savings_summary(db: AsyncSession, months: int = 6):
    """
    Returns total savings and breakdown by month/account/service.
    """
    query = text("""
        SELECT 
            date_trunc('month', s.implemented_at) AS month,
            a.account_name,
            sv.service_name,
            SUM(s.actual_savings) AS total_savings
        FROM savings s
        JOIN resources r ON s.resource_id = r.resource_id
        JOIN accounts a ON r.account_id = a.account_id
        JOIN services sv ON r.service_id = sv.service_id
        WHERE s.implemented_at >= NOW() - INTERVAL :months || ' month'
        GROUP BY month, a.account_name, sv.service_name
        ORDER BY month DESC, total_savings DESC
    """)
    result = await db.execute(query, {"months": months})
    return result.mappings().all()
