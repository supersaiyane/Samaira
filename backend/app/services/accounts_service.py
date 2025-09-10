from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from app.models.accounts import Account
from app.schemas.accounts import AccountCreate

async def list_accounts(db: AsyncSession):
    result = await db.execute(select(Account))
    return result.scalars().all()

async def get_account(db: AsyncSession, account_id: int):
    result = await db.execute(select(Account).where(Account.account_id == account_id))
    return result.scalars().first()

async def create_account_record(db: AsyncSession, account: AccountCreate):
    new_account = Account(**account.dict())
    db.add(new_account)
    await db.commit()
    await db.refresh(new_account)
    return new_account

async def delete_account(db: AsyncSession, account_id: int):
    result = await db.execute(select(Account).where(Account.account_id == account_id))
    account = result.scalars().first()
    if not account:
        return None
    await db.delete(account)
    await db.commit()
    return account
