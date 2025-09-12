from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from app.core.db import get_db
from app.schemas.ai import AIQueryRequest, AIQueryResponse
from app.services.ai_service import process_query

router = APIRouter()

@router.post("/query", response_model=AIQueryResponse)
async def ai_query(request: AIQueryRequest, db: AsyncSession = Depends(get_db)):
    return await process_query(db, request.query)
