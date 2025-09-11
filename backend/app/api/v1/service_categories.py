from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from app.core.db import get_db
from app.schemas.service_categories import ServiceCategoryCreate, ServiceCategoryResponse
from app.services import service_categories_service

router = APIRouter()

@router.get("/", response_model=list[ServiceCategoryResponse])
async def list_service_categories(db: AsyncSession = Depends(get_db)):
    return await service_categories_service.list_service_categories(db)

@router.get("/{category_id}", response_model=ServiceCategoryResponse)
async def get_service_category(category_id: int, db: AsyncSession = Depends(get_db)):
    category = await service_categories_service.get_service_category(db, category_id)
    if not category:
        raise HTTPException(status_code=404, detail="Service category not found")
    return category

@router.post("/", response_model=ServiceCategoryResponse)
async def create_service_category(category: ServiceCategoryCreate, db: AsyncSession = Depends(get_db)):
    return await service_categories_service.create_service_category(db, category)
