from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from app.core.db import get_db
from app.models.budgets import Budget
from app.schemas.budgets import BudgetCreate, BudgetResponse

router = APIRouter()

@router.get("/", response_model=list[BudgetResponse])
async def list_budgets(db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(Budget))
    budgets = result.scalars().all()
    return budgets

@router.get("/{budget_id}", response_model=BudgetResponse)
async def get_budget(budget_id: int, db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(Budget).where(Budget.budget_id == budget_id))
    budget = result.scalars().first()
    if not budget:
        raise HTTPException(status_code=404, detail="Budget not found")
    return budget

@router.post("/", response_model=BudgetResponse)
async def create_budget(budget: BudgetCreate, db: AsyncSession = Depends(get_db)):
    new_budget = Budget(**budget.dict())
    db.add(new_budget)
    await db.commit()
    await db.refresh(new_budget)
    return new_budget

@router.delete("/{budget_id}")
async def delete_budget(budget_id: int, db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(Budget).where(Budget.budget_id == budget_id))
    budget = result.scalars().first()
    if not budget:
        raise HTTPException(status_code=404, detail="Budget not found")
    await db.delete(budget)
    await db.commit()
    return {"status": "deleted", "budget_id": budget_id}
