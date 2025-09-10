from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from app.core.db import get_db
from app.models.anomalies import Anomaly
from app.schemas.anomalies import AnomalyResponse, AnomalyUpdate

router = APIRouter()

@router.get("/", response_model=list[AnomalyResponse])
async def list_anomalies(status: str | None = None, db: AsyncSession = Depends(get_db)):
    query = select(Anomaly)
    if status:
        query = query.where(Anomaly.status == status)
    result = await db.execute(query)
    anomalies = result.scalars().all()
    return anomalies

@router.get("/{anomaly_id}", response_model=AnomalyResponse)
async def get_anomaly(anomaly_id: int, db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(Anomaly).where(Anomaly.anomaly_id == anomaly_id))
    anomaly = result.scalars().first()
    if not anomaly:
        raise HTTPException(status_code=404, detail="Anomaly not found")
    return anomaly

@router.patch("/{anomaly_id}", response_model=AnomalyResponse)
async def update_anomaly(anomaly_id: int, update: AnomalyUpdate, db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(Anomaly).where(Anomaly.anomaly_id == anomaly_id))
    anomaly = result.scalars().first()
    if not anomaly:
        raise HTTPException(status_code=404, detail="Anomaly not found")
    for field, value in update.dict(exclude_unset=True).items():
        setattr(anomaly, field, value)
    await db.commit()
    await db.refresh(anomaly)
    return anomaly

@router.delete("/{anomaly_id}")
async def delete_anomaly(anomaly_id: int, db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(Anomaly).where(Anomaly.anomaly_id == anomaly_id))
    anomaly = result.scalars().first()
    if not anomaly:
        raise HTTPException(status_code=404, detail="Anomaly not found")
    await db.delete(anomaly)
    await db.commit()
    return {"status": "deleted", "anomaly_id": anomaly_id}
