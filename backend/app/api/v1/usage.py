from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from app.core.db import get_db
from app.schemas.usage import UsageResponse
from app.services import usage_service

router = APIRouter()

@router.get("/", response_model=list[UsageResponse])
async def list_usage(resource_id: int, days: int = 7, db: AsyncSession = Depends(get_db)):
    return await usage_service.list_usage(db, resource_id, days)

@router.get("/{usage_id}", response_model=UsageResponse)
async def get_usage(usage_id: int, db: AsyncSession = Depends(get_db)):
    usage = await usage_service.get_usage(db, usage_id)
    if not usage:
        raise HTTPException(status_code=404, detail="Usage record not found")
    return usage
