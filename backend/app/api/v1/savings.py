from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from app.core.db import get_db
from app.schemas.savings import SavingResponse, SavingSummary
from app.services import savings_service

router = APIRouter()

@router.get("/", response_model=list[SavingResponse])
async def list_savings(db: AsyncSession = Depends(get_db)):
    return await savings_service.list_savings(db)

@router.get("/summary", response_model=SavingSummary)
async def savings_summary(db: AsyncSession = Depends(get_db)):
    return await savings_service.savings_summary(db)

@router.get("/{saving_id}", response_model=SavingResponse)
async def get_saving(saving_id: int, db: AsyncSession = Depends(get_db)):
    saving = await savings_service.get_saving(db, saving_id)
    if not saving:
        raise HTTPException(status_code=404, detail="Saving record not found")
    return saving
