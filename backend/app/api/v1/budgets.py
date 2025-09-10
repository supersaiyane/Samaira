from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from app.core.db import get_db
from app.schemas.budgets import BudgetCreate, BudgetResponse
from app.services import budgets_service

router = APIRouter()

@router.get("/", response_model=list[BudgetResponse])
async def list_budgets(db: AsyncSession = Depends(get_db)):
    return await budgets_service.list_budgets(db)

@router.get("/{budget_id}", response_model=BudgetResponse)
async def get_budget(budget_id: int, db: AsyncSession = Depends(get_db)):
    budget = await budgets_service.get_budget(db, budget_id)
    if not budget:
        raise HTTPException(status_code=404, detail="Budget not found")
    return budget

@router.post("/", response_model=BudgetResponse)
async def create_budget(budget: BudgetCreate, db: AsyncSession = Depends(get_db)):
    return await budgets_service.create_budget(db, budget)

@router.delete("/{budget_id}")
async def delete_budget(budget_id: int, db: AsyncSession = Depends(get_db)):
    budget = await budgets_service.delete_budget(db, budget_id)
    if not budget:
        raise HTTPException(status_code=404, detail="Budget not found")
    return {"status": "deleted", "budget_id": budget_id}
