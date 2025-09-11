from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from app.core.db import get_db
from app.schemas.forecasts import ForecastResponse
from app.services import forecasts_service

router = APIRouter()

@router.get("/", response_model=list[ForecastResponse])
async def list_forecasts(db: AsyncSession = Depends(get_db)):
    return await forecasts_service.list_forecasts(db)

@router.get("/{forecast_id}", response_model=ForecastResponse)
async def get_forecast(forecast_id: int, db: AsyncSession = Depends(get_db)):
    forecast = await forecasts_service.get_forecast(db, forecast_id)
    if not forecast:
        raise HTTPException(status_code=404, detail="Forecast not found")
    return forecast
