from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from app.core.db import get_db
from app.schemas.recommendations import RecommendationCreate, RecommendationResponse, RecommendationUpdate
from app.services import recommendations_service

router = APIRouter()

@router.get("/", response_model=list[RecommendationResponse])
async def list_recommendations(status: str | None = None, db: AsyncSession = Depends(get_db)):
    return await recommendations_service.list_recommendations(db, status)

@router.get("/{rec_id}", response_model=RecommendationResponse)
async def get_recommendation(rec_id: int, db: AsyncSession = Depends(get_db)):
    rec = await recommendations_service.get_recommendation(db, rec_id)
    if not rec:
        raise HTTPException(status_code=404, detail="Recommendation not found")
    return rec

@router.post("/", response_model=RecommendationResponse)
async def create_recommendation(rec: RecommendationCreate, db: AsyncSession = Depends(get_db)):
    return await recommendations_service.create_recommendation(db, rec)

@router.patch("/{rec_id}", response_model=RecommendationResponse)
async def update_recommendation(rec_id: int, update: RecommendationUpdate, db: AsyncSession = Depends(get_db)):
    rec = await recommendations_service.update_recommendation(db, rec_id, update)
    if not rec:
        raise HTTPException(status_code=404, detail="Recommendation not found")
    return rec

@router.delete("/{rec_id}")
async def delete_recommendation(rec_id: int, db: AsyncSession = Depends(get_db)):
    rec = await recommendations_service.delete_recommendation(db, rec_id)
    if not rec:
        raise HTTPException(status_code=404, detail="Recommendation not found")
    return {"status": "deleted", "rec_id": rec_id}
