from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from app.models.budgets import Budget
from app.schemas.budgets import BudgetCreate

async def list_budgets(db: AsyncSession):
    result = await db.execute(select(Budget))
    return result.scalars().all()

async def get_budget(db: AsyncSession, budget_id: int):
    result = await db.execute(select(Budget).where(Budget.budget_id == budget_id))
    return result.scalars().first()

async def create_budget(db: AsyncSession, budget: BudgetCreate):
    new_budget = Budget(**budget.dict())
    db.add(new_budget)
    await db.commit()
    await db.refresh(new_budget)
    return new_budget

async def delete_budget(db: AsyncSession, budget_id: int):
    result = await db.execute(select(Budget).where(Budget.budget_id == budget_id))
    budget = result.scalars().first()
    if not budget:
        return None
    await db.delete(budget)
    await db.commit()
    return budget
