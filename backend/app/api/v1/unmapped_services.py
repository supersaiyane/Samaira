from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from app.core.db import get_db
from app.schemas.unmapped_services import UnmappedServiceResponse
from app.services import unmapped_services_service

router = APIRouter()

@router.get("/", response_model=list[UnmappedServiceResponse])
async def list_unmapped_services(db: AsyncSession = Depends(get_db)):
    return await unmapped_services_service.list_unmapped_services(db)

@router.delete("/{service_id}")
async def delete_unmapped_service(service_id: int, db: AsyncSession = Depends(get_db)):
    service = await unmapped_services_service.delete_unmapped_service(db, service_id)
    if not service:
        raise HTTPException(status_code=404, detail="Unmapped service not found")
    return {"status": "deleted", "service_id": service_id}
