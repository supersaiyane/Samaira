from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from app.core.db import get_db
from app.schemas.instance_catalog import InstanceCatalogResponse
from app.services import instance_catalog_service

router = APIRouter()

@router.get("/", response_model=list[InstanceCatalogResponse])
async def list_instances(family: str | None = None, db: AsyncSession = Depends(get_db)):
    return await instance_catalog_service.list_instances(db, family)

@router.get("/{instance_type}", response_model=InstanceCatalogResponse)
async def get_instance(instance_type: str, db: AsyncSession = Depends(get_db)):
    inst = await instance_catalog_service.get_instance(db, instance_type)
    if not inst:
        raise HTTPException(status_code=404, detail="Instance type not found")
    return inst
