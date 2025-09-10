from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from app.models.logs import Log
from datetime import datetime

async def list_logs(db: AsyncSession, level: str | None, component: str | None, since: datetime | None):
    query = select(Log)
    if level:
        query = query.where(Log.level == level)
    if component:
        query = query.where(Log.component == component)
    if since:
        query = query.where(Log.timestamp >= since)
    result = await db.execute(query.order_by(Log.timestamp.desc()))
    return result.scalars().all()

async def get_log(db: AsyncSession, log_id: int):
    result = await db.execute(select(Log).where(Log.log_id == log_id))
    return result.scalars().first()
