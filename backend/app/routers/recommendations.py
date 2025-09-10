from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from app.core.db import get_db
from app.models.recommendations import Recommendation
from app.schemas.recommendations import RecommendationCreate, RecommendationResponse, RecommendationUpdate

router = APIRouter()

@router.get("/", response_model=list[RecommendationResponse])
async def list_recommendations(status: str | None = None, db: AsyncSession = Depends(get_db)):
    query = select(Recommendation)
    if status:
        query = query.where(Recommendation.status == status)
    result = await db.execute(query)
    recs = result.scalars().all()
    return recs

@router.get("/{rec_id}", response_model=RecommendationResponse)
async def get_recommendation(rec_id: int, db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(Recommendation).where(Recommendation.rec_id == rec_id))
    rec = result.scalars().first()
    if not rec:
        raise HTTPException(status_code=404, detail="Recommendation not found")
    return rec

@router.post("/", response_model=RecommendationResponse)
async def create_recommendation(rec: RecommendationCreate, db: AsyncSession = Depends(get_db)):
    new_rec = Recommendation(**rec.dict())
    db.add(new_rec)
    await db.commit()
    await db.refresh(new_rec)
    return new_rec

@router.patch("/{rec_id}", response_model=RecommendationResponse)
async def update_recommendation(rec_id: int, update: RecommendationUpdate, db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(Recommendation).where(Recommendation.rec_id == rec_id))
    rec = result.scalars().first()
    if not rec:
        raise HTTPException(status_code=404, detail="Recommendation not found")
    for field, value in update.dict(exclude_unset=True).items():
        setattr(rec, field, value)
    await db.commit()
    await db.refresh(rec)
    return rec

@router.delete("/{rec_id}")
async def delete_recommendation(rec_id: int, db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(Recommendation).where(Recommendation.rec_id == rec_id))
    rec = result.scalars().first()
    if not rec:
        raise HTTPException(status_code=404, detail="Recommendation not found")
    await db.delete(rec)
    await db.commit()
    return {"status": "deleted", "rec_id": rec_id}
