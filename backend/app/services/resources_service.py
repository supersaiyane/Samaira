from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from app.models.resources import Resource
from app.schemas.resources import ResourceCreate

async def list_resources(db: AsyncSession, account_id: int | None, service_id: int | None, region: str | None):
    query = select(Resource)
    if account_id:
        query = query.where(Resource.account_id == account_id)
    if service_id:
        query = query.where(Resource.service_id == service_id)
    if region:
        query = query.where(Resource.region == region)
    result = await db.execute(query)
    return result.scalars().all()

async def get_resource(db: AsyncSession, resource_id: int):
    result = await db.execute(select(Resource).where(Resource.resource_id == resource_id))
    return result.scalars().first()

async def create_resource(db: AsyncSession, resource: ResourceCreate):
    new_resource = Resource(**resource.dict())
    db.add(new_resource)
    await db.commit()
    await db.refresh(new_resource)
    return new_resource

async def delete_resource(db: AsyncSession, resource_id: int):
    result = await db.execute(select(Resource).where(Resource.resource_id == resource_id))
    resource = result.scalars().first()
    if not resource:
        return None
    await db.delete(resource)
    await db.commit()
    return resource
