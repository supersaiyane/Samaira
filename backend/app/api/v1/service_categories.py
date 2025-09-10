from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from app.core.db import get_db
from app.models.service_categories import ServiceCategory
from app.schemas.service_categories import ServiceCategoryCreate, ServiceCategoryResponse

router = APIRouter()

@router.get("/", response_model=list[ServiceCategoryResponse])
async def list_service_categories(db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(ServiceCategory))
    return result.scalars().all()

@router.get("/{category_id}", response_model=ServiceCategoryResponse)
async def get_service_category(category_id: int, db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(ServiceCategory).where(ServiceCategory.category_id == category_id))
    category = result.scalars().first()
    if not category:
        raise HTTPException(status_code=404, detail="Service category not found")
    return category

@router.post("/", response_model=ServiceCategoryResponse)
async def create_service_category(category: ServiceCategoryCreate, db: AsyncSession = Depends(get_db)):
    new_category = ServiceCategory(**category.dict())
    db.add(new_category)
    await db.commit()
    await db.refresh(new_category)
    return new_category
