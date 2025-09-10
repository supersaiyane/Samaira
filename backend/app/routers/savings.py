from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select, func
from app.core.db import get_db
from app.models.savings import Saving
from app.schemas.savings import SavingResponse, SavingSummary

router = APIRouter()

@router.get("/", response_model=list[SavingResponse])
async def list_savings(db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(Saving))
    savings = result.scalars().all()
    return savings

@router.get("/summary", response_model=SavingSummary)
async def savings_summary(db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(func.sum(Saving.actual_savings)))
    total = result.scalar() or 0.0
    return {"total_savings": total, "currency": "USD"}

@router.get("/{saving_id}", response_model=SavingResponse)
async def get_saving(saving_id: int, db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(Saving).where(Saving.saving_id == saving_id))
    saving = result.scalars().first()
    if not saving:
        raise HTTPException(status_code=404, detail="Saving record not found")
    return saving
