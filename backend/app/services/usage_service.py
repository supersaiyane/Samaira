from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from app.models.usage import Usage
from datetime import datetime, timedelta

async def list_usage(db: AsyncSession, resource_id: int, days: int):
    since = datetime.utcnow() - timedelta(days=days)
    query = select(Usage).where(
        Usage.resource_id == resource_id,
        Usage.collected_at >= since
    ).order_by(Usage.collected_at.desc())
    result = await db.execute(query)
    return result.scalars().all()

async def get_usage(db: AsyncSession, usage_id: int):
    result = await db.execute(select(Usage).where(Usage.usage_id == usage_id))
    return result.scalars().first()
