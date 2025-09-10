from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from app.core.db import get_db
from app.models.resources import Resource
from app.schemas.resources import ResourceCreate, ResourceResponse

router = APIRouter()

@router.get("/", response_model=list[ResourceResponse])
async def list_resources(
    account_id: int | None = None,
    service_id: int | None = None,
    region: str | None = None,
    db: AsyncSession = Depends(get_db)
):
    query = select(Resource)
    if account_id:
        query = query.where(Resource.account_id == account_id)
    if service_id:
        query = query.where(Resource.service_id == service_id)
    if region:
        query = query.where(Resource.region == region)
    result = await db.execute(query)
    return result.scalars().all()

@router.get("/{resource_id}", response_model=ResourceResponse)
async def get_resource(resource_id: int, db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(Resource).where(Resource.resource_id == resource_id))
    resource = result.scalars().first()
    if not resource:
        raise HTTPException(status_code=404, detail="Resource not found")
    return resource

@router.post("/", response_model=ResourceResponse)
async def create_resource(resource: ResourceCreate, db: AsyncSession = Depends(get_db)):
    new_resource = Resource(**resource.dict())
    db.add(new_resource)
    await db.commit()
    await db.refresh(new_resource)
    return new_resource

@router.delete("/{resource_id}")
async def delete_resource(resource_id: int, db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(Resource).where(Resource.resource_id == resource_id))
    resource = result.scalars().first()
    if not resource:
        raise HTTPException(status_code=404, detail="Resource not found")
    await db.delete(resource)
    await db.commit()
    return {"status": "deleted", "resource_id": resource_id}
