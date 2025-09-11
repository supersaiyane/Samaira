from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from app.core.db import get_db
from app.schemas.insights import InsightResponse
from app.services import insights_service

router = APIRouter()

@router.get("/", response_model=list[InsightResponse])
async def list_insights(db: AsyncSession = Depends(get_db)):
    return await insights_service.list_insights(db)

@router.get("/{insight_id}", response_model=InsightResponse)
async def get_insight(insight_id: int, db: AsyncSession = Depends(get_db)):
    insight = await insights_service.get_insight(db, insight_id)
    if not insight:
        raise HTTPException(status_code=404, detail="Insight not found")
    return insight
