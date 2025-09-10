from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from app.models.services import Service
from app.schemas.services import ServiceCreate

async def list_services(db: AsyncSession):
    result = await db.execute(select(Service))
    return result.scalars().all()

async def get_service(db: AsyncSession, service_id: int):
    result = await db.execute(select(Service).where(Service.service_id == service_id))
    return result.scalars().first()

async def create_service(db: AsyncSession, service: ServiceCreate):
    new_service = Service(**service.dict())
    db.add(new_service)
    await db.commit()
    await db.refresh(new_service)
    return new_service

async def delete_service(db: AsyncSession, service_id: int):
    result = await db.execute(select(Service).where(Service.service_id == service_id))
    service = result.scalars().first()
    if not service:
        return None
    await db.delete(service)
    await db.commit()
    return service
