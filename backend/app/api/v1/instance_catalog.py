from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from app.core.db import get_db
from app.models.instance_catalog import InstanceCatalog
from app.schemas.instance_catalog import InstanceCatalogResponse

router = APIRouter()

@router.get("/", response_model=list[InstanceCatalogResponse])
async def list_instances(family: str | None = None, db: AsyncSession = Depends(get_db)):
    query = select(InstanceCatalog)
    if family:
        query = query.where(InstanceCatalog.family == family)
    result = await db.execute(query)
    return result.scalars().all()

@router.get("/{instance_type}", response_model=InstanceCatalogResponse)
async def get_instance(instance_type: str, db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(InstanceCatalog).where(InstanceCatalog.instance_type == instance_type))
    inst = result.scalars().first()
    if not inst:
        raise HTTPException(status_code=404, detail="Instance type not found")
    return inst
