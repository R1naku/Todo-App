from datetime import datetime
from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select, or_, update as sa_update, delete as sa_delete
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import joinedload
from sqlalchemy import func

from register import get_current_user, TelegramUser
from models import Plan, PlanCreate, PlanUpdate, DBPlan, ShareTask
from database import get_db

router = APIRouter(prefix="/plans", tags=["plans"])

@router.post("", response_model=Plan)
async def create_plan(plan: PlanCreate, current_user: TelegramUser = Depends(get_current_user), db: AsyncSession = Depends(get_db)):
    new_plan = DBPlan(
        title=plan.title,
        owner_id=current_user.id,
        shared_with=[],
        created_at=datetime.utcnow(),
        updated_at=datetime.utcnow()
    )
    db.add(new_plan)
    await db.commit()
    await db.refresh(new_plan)
    return Plan.model_validate(new_plan)

@router.get("", response_model=List[Plan])
async def list_plans(current_user: TelegramUser = Depends(get_current_user), db: AsyncSession = Depends(get_db)):
    stmt = select(DBPlan).options(joinedload(DBPlan.tasks).joinedload(DBTask.sub_tasks)).where(
        or_(DBPlan.owner_id == current_user.id, DBPlan.shared_with.contains([current_user.id]))
    )
    result = await db.execute(stmt)
    db_plans = result.unique().scalars().all()
    return [Plan.model_validate(p) for p in db_plans]

@router.get("/{plan_id}", response_model=Plan)
async def get_plan(plan_id: int, current_user: TelegramUser = Depends(get_current_user), db: AsyncSession = Depends(get_db)):
    stmt = select(DBPlan).options(joinedload(DBPlan.tasks).joinedload(DBTask.sub_tasks)).where(DBPlan.id == plan_id)
    result = await db.execute(stmt)
    p = result.scalar_one_or_none()
    if p is None or (p.owner_id != current_user.id and current_user.id not in p.shared_with):
        raise HTTPException(status_code=404, detail="Plan not found")
    return Plan.model_validate(p)