from fastapi import FastAPI, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from app.core.db import get_db
from app.models.accounts import Account

app = FastAPI()

@app.get("/accounts")
async def list_accounts(db: AsyncSession = Depends(get_db)):
    result = await db.execute("SELECT * FROM accounts LIMIT 10;")
    return result.mappings().all()
