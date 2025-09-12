from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from app.core.db import get_db
from sqlalchemy.future import select
from app.models.ai_queries_log import AIQueryLog

router = APIRouter()

@router.get("/logs")
async def list_ai_logs(db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(AIQueryLog).order_by(AIQueryLog.created_at.desc()))
    return result.scalars().all()
