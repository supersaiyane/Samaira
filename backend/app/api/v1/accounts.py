from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from app.core.db import get_db
from app.schemas.accounts import AccountResponse, AccountCreate
from app.services import accounts_service

router = APIRouter()

@router.get("/", response_model=list[AccountResponse])
async def list_accounts(db: AsyncSession = Depends(get_db)):
    return await accounts_service.list_accounts(db)

@router.get("/{account_id}", response_model=AccountResponse)
async def get_account(account_id: int, db: AsyncSession = Depends(get_db)):
    account = await accounts_service.get_account(db, account_id)
    if not account:
        raise HTTPException(status_code=404, detail="Account not found")
    return account

@router.post("/", response_model=AccountResponse)
async def create_account(account: AccountCreate, db: AsyncSession = Depends(get_db)):
    return await accounts_service.create_account_record(db, account)

@router.delete("/{account_id}")
async def delete_account(account_id: int, db: AsyncSession = Depends(get_db)):
    account = await accounts_service.delete_account(db, account_id)
    if not account:
        raise HTTPException(status_code=404, detail="Account not found")
    return {"status": "deleted", "account_id": account_id}
