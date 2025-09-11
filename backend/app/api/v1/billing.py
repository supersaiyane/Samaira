from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from app.core.db import get_db
from app.schemas.billing import BillingResponse
from app.services import billing_service
from datetime import date

router = APIRouter()

@router.get("/", response_model=list[BillingResponse])
async def list_billing(account_id: int | None = None, service_id: int | None = None, resource_id: int | None = None, start_date: date | None = None, end_date: date | None = None, db: AsyncSession = Depends(get_db)):
    return await billing_service.list_billing(db, account_id, service_id, resource_id, start_date, end_date)

@router.get("/{billing_id}", response_model=BillingResponse)
async def get_billing(billing_id: int, db: AsyncSession = Depends(get_db)):
    billing = await billing_service.get_billing(db, billing_id)
    if not billing:
        raise HTTPException(status_code=404, detail="Billing record not found")
    return billing
