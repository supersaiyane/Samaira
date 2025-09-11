from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from app.models.insights import Insight

async def list_insights(db: AsyncSession):
    result = await db.execute(select(Insight).order_by(Insight.created_at.desc()))
    return result.scalars().all()

async def get_insight(db: AsyncSession, insight_id: int):
    result = await db.execute(select(Insight).where(Insight.insight_id == insight_id))
    return result.scalars().first()
