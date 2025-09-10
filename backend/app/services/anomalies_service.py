from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from app.models.anomalies import Anomaly
from app.schemas.anomalies import AnomalyUpdate

async def list_anomalies(db: AsyncSession, status: str | None = None):
    query = select(Anomaly)
    if status:
        query = query.where(Anomaly.status == status)
    result = await db.execute(query)
    return result.scalars().all()

async def get_anomaly(db: AsyncSession, anomaly_id: int):
    result = await db.execute(select(Anomaly).where(Anomaly.anomaly_id == anomaly_id))
    return result.scalars().first()

async def update_anomaly(db: AsyncSession, anomaly_id: int, update: AnomalyUpdate):
    result = await db.execute(select(Anomaly).where(Anomaly.anomaly_id == anomaly_id))
    anomaly = result.scalars().first()
    if not anomaly:
        return None
    for field, value in update.dict(exclude_unset=True).items():
        setattr(anomaly, field, value)
    await db.commit()
    await db.refresh(anomaly)
    return anomaly

async def delete_anomaly(db: AsyncSession, anomaly_id: int):
    result = await db.execute(select(Anomaly).where(Anomaly.anomaly_id == anomaly_id))
    anomaly = result.scalars().first()
    if not anomaly:
        return None
    await db.delete(anomaly)
    await db.commit()
    return anomaly
