from datetime import datetime
from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy import select, or_, update as sa_update, delete as sa_delete
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import func
from sqlalchemy.orm import joinedload

from register import get_current_user, TelegramUser
from models import Task, TaskCreate, TaskUpdate, TaskAnalysis, ShareTask, TaskBase, DBTask
from database import get_db

# ... остальной код остается таким же

from register import get_current_user, TelegramUser
from models import Task, TaskCreate, TaskUpdate, TaskAnalysis, ShareTask, TaskBase, DBTask
from database import get_db

router = APIRouter(prefix="/tasks", tags=["tasks"])

def analyze_task(title: str, description: Optional[str]) -> TaskAnalysis:
    combined = f"{title} {description or ''}".lower()
    if "urgent" in combined or "important" in combined:
        suggested_priority = "high"
        advice = "Эта задача кажется срочной. Приоритизируйте её немедленно."
    elif "later" in combined:
        suggested_priority = "low"
        advice = "Это можно сделать позже. Нет спешки."
    else:
        suggested_priority = "medium"
        advice = "Стандартный приоритет. Запланируйте соответственно."
    return TaskAnalysis(advice=advice, suggested_priority=suggested_priority)

@router.post("", response_model=Task)
async def create_task(task: TaskCreate, current_user: TelegramUser = Depends(get_current_user), db: AsyncSession = Depends(get_db)):
    analysis = analyze_task(task.title, task.description)
    new_task = DBTask(
        title=task.title,
        description=task.description,
        due_date=task.due_date,
        priority=analysis.suggested_priority,
        owner_id=current_user.id,
        shared_with=[],
        created_at=datetime.utcnow(),
        updated_at=datetime.utcnow(),
        plan_id=task.plan_id,
        parent_id=task.parent_id,
        completed=task.completed
    )
    db.add(new_task)
    await db.commit()
    await db.refresh(new_task)
    return Task.model_validate(new_task)

@router.post("/analyze-task", response_model=TaskAnalysis)
async def analyze_new_task(task: TaskBase, current_user: TelegramUser = Depends(get_current_user)):
    return analyze_task(task.title, task.description)

@router.get("", response_model=List[Task])
async def list_tasks(
    filter_plan_id: Optional[int] = Query(None, description="Filter by plan_id; use 0 for tasks without plan"),
    current_user: TelegramUser = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    stmt = select(DBTask).options(joinedload(DBTask.sub_tasks)).where(
        or_(DBTask.owner_id == current_user.id, DBTask.shared_with.contains([current_user.id]))
    )
    if filter_plan_id is not None:
        if filter_plan_id == 0:
            stmt = stmt.where(DBTask.plan_id.is_(None))
        else:
            stmt = stmt.where(DBTask.plan_id == filter_plan_id)
    result = await db.execute(stmt)
    db_tasks = result.unique().scalars().all()
    return [Task.model_validate(t) for t in db_tasks]

@router.get("/{task_id}", response_model=Task)
async def get_task(task_id: int, current_user: TelegramUser = Depends(get_current_user), db: AsyncSession = Depends(get_db)):
    stmt = select(DBTask).options(joinedload(DBTask.sub_tasks)).where(DBTask.id == task_id)
    result = await db.execute(stmt)
    t = result.scalar_one_or_none()
    if t is None or (t.owner_id != current_user.id and current_user.id not in t.shared_with):
        raise HTTPException(status_code=404, detail="Task not found")
    return Task.model_validate(t)

@router.put("/{task_id}", response_model=Task)
async def update_task(task_id: int, update_data: TaskUpdate, current_user: TelegramUser = Depends(get_current_user), db: AsyncSession = Depends(get_db)):
    stmt = select(DBTask).where(DBTask.id == task_id, DBTask.owner_id == current_user.id)
    result = await db.execute(stmt)
    t = result.scalar_one_or_none()
    if t is None:
        raise HTTPException(status_code=404, detail="Task not found or not authorized")

    update_dict = update_data.dict(exclude_unset=True)
    if "title" in update_dict or "description" in update_dict:
        new_title = update_dict.get("title", t.title)
        new_desc = update_dict.get("description", t.description)
        analysis = analyze_task(new_title, new_desc)
        update_dict["priority"] = analysis.suggested_priority

    update_dict["updated_at"] = datetime.utcnow()
    await db.execute(sa_update(DBTask).where(DBTask.id == task_id).values(**update_dict))
    await db.commit()
    await db.refresh(t)
    return Task.model_validate(t)

@router.delete("/{task_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_task(task_id: int, current_user: TelegramUser = Depends(get_current_user), db: AsyncSession = Depends(get_db)):
    stmt = sa_delete(DBTask).where(DBTask.id == task_id, DBTask.owner_id == current_user.id)
    result = await db.execute(stmt)
    if result.rowcount == 0:
        raise HTTPException(status_code=404, detail="Task not found or not authorized")
    await db.commit()

@router.post("/{task_id}/share", response_model=Task)
async def share_task(task_id: int, share: ShareTask, current_user: TelegramUser = Depends(get_current_user), db: AsyncSession = Depends(get_db)):
    stmt = select(DBTask).where(DBTask.id == task_id, DBTask.owner_id == current_user.id)
    result = await db.execute(stmt)
    t = result.scalar_one_or_none()
    if t is None:
        raise HTTPException(status_code=404, detail="Task not found or not authorized")

    await db.execute(
        sa_update(DBTask)
        .where(DBTask.id == task_id)
        .values(
            shared_with=func.array_append(DBTask.shared_with, share.user_id),
            updated_at=datetime.utcnow()
        )
    )
    await db.commit()
    await db.refresh(t)
    return Task.model_validate(t)