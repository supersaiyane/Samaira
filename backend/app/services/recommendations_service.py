from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from app.models.recommendations import Recommendation
from app.schemas.recommendations import RecommendationCreate, RecommendationUpdate

async def list_recommendations(db: AsyncSession, status: str | None = None):
    query = select(Recommendation)
    if status:
        query = query.where(Recommendation.status == status)
    result = await db.execute(query)
    return result.scalars().all()

async def get_recommendation(db: AsyncSession, rec_id: int):
    result = await db.execute(select(Recommendation).where(Recommendation.rec_id == rec_id))
    return result.scalars().first()

async def create_recommendation(db: AsyncSession, rec: RecommendationCreate):
    new_rec = Recommendation(**rec.dict())
    db.add(new_rec)
    await db.commit()
    await db.refresh(new_rec)
    return new_rec

async def update_recommendation(db: AsyncSession, rec_id: int, update: RecommendationUpdate):
    result = await db.execute(select(Recommendation).where(Recommendation.rec_id == rec_id))
    rec = result.scalars().first()
    if not rec:
        return None
    for field, value in update.dict(exclude_unset=True).items():
        setattr(rec, field, value)
    await db.commit()
    await db.refresh(rec)
    return rec

async def delete_recommendation(db: AsyncSession, rec_id: int):
    result = await db.execute(select(Recommendation).where(Recommendation.rec_id == rec_id))
    rec = result.scalars().first()
    if not rec:
        return None
    await db.delete(rec)
    await db.commit()
    return rec
