from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from app.core.db import get_db
from app.models.unmapped_services import UnmappedService
from app.schemas.unmapped_services import UnmappedServiceResponse

router = APIRouter()

@router.get("/", response_model=list[UnmappedServiceResponse])
async def list_unmapped_services(db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(UnmappedService))
    return result.scalars().all()

@router.delete("/{service_id}")
async def delete_unmapped_service(service_id: int, db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(UnmappedService).where(UnmappedService.service_id == service_id))
    service = result.scalars().first()
    if not service:
        raise HTTPException(status_code=404, detail="Unmapped service not found")
    await db.delete(service)
    await db.commit()
    return {"status": "deleted", "service_id": service_id}
