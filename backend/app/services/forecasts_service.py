from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from app.models.forecasts import Forecast

async def list_forecasts(db: AsyncSession):
    result = await db.execute(select(Forecast))
    return result.scalars().all()

async def get_forecast(db: AsyncSession, forecast_id: int):
    result = await db.execute(select(Forecast).where(Forecast.forecast_id == forecast_id))
    return result.scalars().first()
