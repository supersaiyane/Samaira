from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from app.models.unmapped_services import UnmappedService

async def list_unmapped_services(db: AsyncSession):
    result = await db.execute(select(UnmappedService))
    return result.scalars().all()

async def delete_unmapped_service(db: AsyncSession, service_id: int):
    result = await db.execute(select(UnmappedService).where(UnmappedService.service_id == service_id))
    service = result.scalars().first()
    if not service:
        return None
    await db.delete(service)
    await db.commit()
    return service
