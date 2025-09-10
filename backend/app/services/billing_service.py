from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from app.models.billing import Billing
from datetime import date

async def list_billing(db: AsyncSession, account_id: int | None, service_id: int | None, resource_id: int | None, start_date: date | None, end_date: date | None):
    query = select(Billing)
    if account_id:
        query = query.where(Billing.account_id == account_id)
    if service_id:
        query = query.where(Billing.service_id == service_id)
    if resource_id:
        query = query.where(Billing.resource_id == resource_id)
    if start_date:
        query = query.where(Billing.usage_date >= start_date)
    if end_date:
        query = query.where(Billing.usage_date <= end_date)
    result = await db.execute(query.order_by(Billing.usage_date.desc()))
    return result.scalars().all()

async def get_billing(db: AsyncSession, billing_id: int):
    result = await db.execute(select(Billing).where(Billing.billing_id == billing_id))
    return result.scalars().first()
