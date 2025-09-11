from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from app.core.db import get_db
from app.schemas.logs import LogResponse
from app.services import logs_service
from datetime import datetime

router = APIRouter()

@router.get("/", response_model=list[LogResponse])
async def list_logs(level: str | None = None, component: str | None = None, since: datetime | None = None, db: AsyncSession = Depends(get_db)):
    return await logs_service.list_logs(db, level, component, since)

@router.get("/{log_id}", response_model=LogResponse)
async def get_log(log_id: int, db: AsyncSession = Depends(get_db)):
    log = await logs_service.get_log(db, log_id)
    if not log:
        raise HTTPException(status_code=404, detail="Log not found")
    return log
