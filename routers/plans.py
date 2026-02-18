from datetime import datetime
from typing import List

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select, or_, update as sa_update
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import joinedload

from database import get_db
from models import DBPlan, DBTask  # Добавьте DBTask сюда!
from register import get_current_user, TelegramUser
from schemas import Plan, PlanCreate, PlanUpdate

router = APIRouter(prefix="/plans", tags=["plans"])


@router.post("", response_model=Plan)
async def create_plan(
    plan: PlanCreate,
    current_user: TelegramUser = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
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
async def list_plans(
    current_user: TelegramUser = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    stmt = select(DBPlan).options(
        joinedload(DBPlan.tasks).joinedload(DBTask.sub_tasks)
    ).where(
        or_(
            DBPlan.owner_id == current_user.id,
            DBPlan.shared_with.contains([current_user.id])
        )
    )
    result = await db.execute(stmt)
    db_plans = result.unique().scalars().all()
    return [Plan.model_validate(p) for p in db_plans]


@router.get("/{plan_id}", response_model=Plan)
async def get_plan(
    plan_id: int,
    current_user: TelegramUser = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    stmt = select(DBPlan).options(
        joinedload(DBPlan.tasks).joinedload(DBTask.sub_tasks)
    ).where(DBPlan.id == plan_id)

    result = await db.execute(stmt)
    p = result.scalar_one_or_none()

    if p is None or (p.owner_id != current_user.id and current_user.id not in p.shared_with):
        raise HTTPException(status_code=404, detail="План не найден")

    return Plan.model_validate(p)


@router.put("/{plan_id}", response_model=Plan)
async def update_plan(
    plan_id: int,
    update_data: PlanUpdate,
    current_user: TelegramUser = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    stmt = select(DBPlan).where(
        DBPlan.id == plan_id,
        DBPlan.owner_id == current_user.id
    )
    result = await db.execute(stmt)
    plan = result.scalar_one_or_none()

    if plan is None:
        raise HTTPException(
            status_code=404,
            detail="План не найден или вы не являетесь владельцем"
        )

    update_dict = update_data.dict(exclude_unset=True)
    update_dict["updated_at"] = datetime.utcnow()

    await db.execute(
        sa_update(DBPlan)
        .where(DBPlan.id == plan_id)
        .values(**update_dict)
    )
    await db.commit()
    await db.refresh(plan)

    return Plan.model_validate(plan)