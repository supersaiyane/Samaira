from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from sqlalchemy import and_
from app.core.db import get_db
from app.models.billing import Billing
from app.schemas.billing import BillingResponse
from datetime import date

router = APIRouter()

@router.get("/", response_model=list[BillingResponse])
async def list_billing(
    account_id: int | None = None,
    service_id: int | None = None,
    resource_id: int | None = None,
    start_date: date | None = None,
    end_date: date | None = None,
    db: AsyncSession = Depends(get_db)
):
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

    query = query.order_by(Billing.usage_date.desc())

    result = await db.execute(query)
    return result.scalars().all()

@router.get("/{billing_id}", response_model=BillingResponse)
async def get_billing(billing_id: int, db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(Billing).where(Billing.billing_id == billing_id))
    billing = result.scalars().first()
    if not billing:
        raise HTTPException(status_code=404, detail="Billing record not found")
    return billing
