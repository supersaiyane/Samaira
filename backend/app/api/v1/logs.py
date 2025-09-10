from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from app.core.db import get_db
from app.models.logs import Log
from app.schemas.logs import LogResponse
from datetime import datetime

router = APIRouter()

@router.get("/", response_model=list[LogResponse])
async def list_logs(
    level: str | None = None,
    component: str | None = None,
    since: datetime | None = None,
    db: AsyncSession = Depends(get_db)
):
    query = select(Log)
    if level:
        query = query.where(Log.level == level)
    if component:
        query = query.where(Log.component == component)
    if since:
        query = query.where(Log.timestamp >= since)
    query = query.order_by(Log.timestamp.desc())

    result = await db.execute(query)
    return result.scalars().all()

@router.get("/{log_id}", response_model=LogResponse)
async def get_log(log_id: int, db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(Log).where(Log.log_id == log_id))
    log = result.scalars().first()
    if not log:
        raise HTTPException(status_code=404, detail="Log not found")
    return log
