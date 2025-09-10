from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from app.models.service_categories import ServiceCategory
from app.schemas.service_categories import ServiceCategoryCreate

async def list_service_categories(db: AsyncSession):
    result = await db.execute(select(ServiceCategory))
    return result.scalars().all()

async def get_service_category(db: AsyncSession, category_id: int):
    result = await db.execute(select(ServiceCategory).where(ServiceCategory.category_id == category_id))
    return result.scalars().first()

async def create_service_category(db: AsyncSession, category: ServiceCategoryCreate):
    new_category = ServiceCategory(**category.dict())
    db.add(new_category)
    await db.commit()
    await db.refresh(new_category)
    return new_category
