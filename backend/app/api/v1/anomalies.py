from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from app.core.db import get_db
from app.schemas.anomalies import AnomalyResponse, AnomalyUpdate
from app.services import anomalies_service

router = APIRouter()

@router.get("/", response_model=list[AnomalyResponse])
async def list_anomalies(status: str | None = None, db: AsyncSession = Depends(get_db)):
    return await anomalies_service.list_anomalies(db, status)

@router.get("/{anomaly_id}", response_model=AnomalyResponse)
async def get_anomaly(anomaly_id: int, db: AsyncSession = Depends(get_db)):
    anomaly = await anomalies_service.get_anomaly(db, anomaly_id)
    if not anomaly:
        raise HTTPException(status_code=404, detail="Anomaly not found")
    return anomaly

@router.patch("/{anomaly_id}", response_model=AnomalyResponse)
async def update_anomaly(anomaly_id: int, update: AnomalyUpdate, db: AsyncSession = Depends(get_db)):
    anomaly = await anomalies_service.update_anomaly(db, anomaly_id, update)
    if not anomaly:
        raise HTTPException(status_code=404, detail="Anomaly not found")
    return anomaly

@router.delete("/{anomaly_id}")
async def delete_anomaly(anomaly_id: int, db: AsyncSession = Depends(get_db)):
    anomaly = await anomalies_service.delete_anomaly(db, anomaly_id)
    if not anomaly:
        raise HTTPException(status_code=404, detail="Anomaly not found")
    return {"status": "deleted", "anomaly_id": anomaly_id}
