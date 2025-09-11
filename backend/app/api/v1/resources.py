from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from app.core.db import get_db
from app.schemas.resources import ResourceCreate, ResourceResponse
from app.services import resources_service

router = APIRouter()

@router.get("/", response_model=list[ResourceResponse])
async def list_resources(account_id: int | None = None, service_id: int | None = None, region: str | None = None, db: AsyncSession = Depends(get_db)):
    return await resources_service.list_resources(db, account_id, service_id, region)

@router.get("/{resource_id}", response_model=ResourceResponse)
async def get_resource(resource_id: int, db: AsyncSession = Depends(get_db)):
    resource = await resources_service.get_resource(db, resource_id)
    if not resource:
        raise HTTPException(status_code=404, detail="Resource not found")
    return resource

@router.post("/", response_model=ResourceResponse)
async def create_resource(resource: ResourceCreate, db: AsyncSession = Depends(get_db)):
    return await resources_service.create_resource(db, resource)

@router.delete("/{resource_id}")
async def delete_resource(resource_id: int, db: AsyncSession = Depends(get_db)):
    resource = await resources_service.delete_resource(db, resource_id)
    if not resource:
        raise HTTPException(status_code=404, detail="Resource not found")
    return {"status": "deleted", "resource_id": resource_id}
