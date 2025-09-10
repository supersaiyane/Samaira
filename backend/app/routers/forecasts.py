from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from app.core.db import get_db
from app.models.forecasts import Forecast
from app.schemas.forecasts import ForecastResponse

router = APIRouter()

@router.get("/", response_model=list[ForecastResponse])
async def list_forecasts(db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(Forecast))
    forecasts = result.scalars().all()
    return forecasts

@router.get("/{forecast_id}", response_model=ForecastResponse)
async def get_forecast(forecast_id: int, db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(Forecast).where(Forecast.forecast_id == forecast_id))
    forecast = result.scalars().first()
    if not forecast:
        raise HTTPException(status_code=404, detail="Forecast not found")
    return forecast
