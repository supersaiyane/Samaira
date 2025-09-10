from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select, func
from app.models.savings import Saving

async def list_savings(db: AsyncSession):
    result = await db.execute(select(Saving))
    return result.scalars().all()

async def get_saving(db: AsyncSession, saving_id: int):
    result = await db.execute(select(Saving).where(Saving.saving_id == saving_id))
    return result.scalars().first()

async def savings_summary(db: AsyncSession):
    result = await db.execute(select(func.sum(Saving.actual_savings)))
    total = result.scalar() or 0.0
    return {"total_savings": total, "currency": "USD"}
