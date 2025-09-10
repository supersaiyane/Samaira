from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from app.models.instance_catalog import InstanceCatalog

async def list_instances(db: AsyncSession, family: str | None):
    query = select(InstanceCatalog)
    if family:
        query = query.where(InstanceCatalog.family == family)
    result = await db.execute(query)
    return result.scalars().all()

async def get_instance(db: AsyncSession, instance_type: str):
    result = await db.execute(select(InstanceCatalog).where(InstanceCatalog.instance_type == instance_type))
    return result.scalars().first()
