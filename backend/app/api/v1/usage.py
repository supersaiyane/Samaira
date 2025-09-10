from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from app.core.db import get_db
from app.models.usage import Usage
from app.schemas.usage import UsageResponse
from datetime import datetime, timedelta

router = APIRouter()

@router.get("/", response_model=list[UsageResponse])
async def list_usage(
    resource_id: int,
    days: int = 7,
    db: AsyncSession = Depends(get_db)
):
    since = datetime.utcnow() - timedelta(days=days)
    query = select(Usage).where(
        Usage.resource_id == resource_id,
        Usage.collected_at >= since
    ).order_by(Usage.collected_at.desc())
    result = await db.execute(query)
    return result.scalars().all()

@router.get("/{usage_id}", response_model=UsageResponse)
async def get_usage(usage_id: int, db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(Usage).where(Usage.usage_id == usage_id))
    usage = result.scalars().first()
    if not usage:
        raise HTTPException(status_code=404, detail="Usage record not found")
    return usage
