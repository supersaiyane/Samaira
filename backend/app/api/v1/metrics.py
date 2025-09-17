from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import text
from app.db import get_db

router = APIRouter()

@router.get("/anomalies/count")
async def anomalies_count(db: AsyncSession = Depends(get_db)):
    """Return total count of anomalies"""
    q = text("SELECT COUNT(*) AS count FROM anomalies")
    result = await db.execute(q)
    row = result.mappings().first()
    return {"count": row["count"] if row else 0}


@router.get("/savings/total")
async def savings_total(db: AsyncSession = Depends(get_db)):
    """Return total realized savings (numeric)"""
    q = text("SELECT COALESCE(SUM(actual_savings), 0) AS total FROM savings")
    result = await db.execute(q)
    row = result.mappings().first()
    return {"total": float(row["total"]) if row else 0.0}


@router.get("/budgets/breaches")
async def budget_breaches(db: AsyncSession = Depends(get_db)):
    """Return count of budgets breached in the current month"""
    q = text("""
        SELECT COUNT(*) AS breaches
        FROM budgets b
        WHERE EXISTS (
            SELECT 1 FROM billing bl
            WHERE (bl.account_id = b.account_id OR b.account_id IS NULL)
              AND (bl.service_id = b.service_id OR b.service_id IS NULL)
              AND date_trunc('month', bl.usage_date) = date_trunc('month', CURRENT_DATE)
            GROUP BY bl.account_id, bl.service_id
            HAVING SUM(bl.cost_amount) > b.budget_limit
        )
    """)
    result = await db.execute(q)
    row = result.mappings().first()
    return {"breaches": row["breaches"] if row else 0}


@router.get("/clusters/count")
async def get_clusters_count(db: AsyncSession = Depends(get_db)):
    q = "SELECT COUNT(*) FROM clusters WHERE status = 'active';"
    result = await db.execute(text(q))
    return {"count": result.scalar() or 0}

@router.get("/ec2/idle")
async def get_idle_ec2_count(db: AsyncSession = Depends(get_db)):
    q = "SELECT COUNT(*) FROM ec2_instances WHERE utilization < 10;"
    result = await db.execute(text(q))
    return {"idle": result.scalar() or 0}