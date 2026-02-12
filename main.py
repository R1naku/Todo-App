from fastapi import FastAPI, Depends
import uvicorn
from datetime import datetime, timedelta

from routers.tasks import router as tasks_router
from database import engine, Base, get_db
from register import TelegramUser, get_current_user
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, or_
from models import DBTask, Task

app = FastAPI(
    title="Telegram Task Mini App",
    description="API for managing tasks in a Telegram mini app with analysis and sharing features.",
    version="0.1.0"
)

app.include_router(tasks_router, prefix="/tasks", tags=["tasks"])

import asyncio
async def init_db():
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

@app.on_event("startup")
async def startup():
    await init_db()

@app.get("/reminders")
async def check_reminders(current_user: TelegramUser = Depends(get_current_user), db: AsyncSession = Depends(get_db)):
    stmt = select(DBTask).where(
        or_(DBTask.owner_id == current_user.id, DBTask.shared_with.contains([current_user.id]))
    ).where(DBTask.due_date < datetime.utcnow() + timedelta(hours=1))
    result = await db.execute(stmt)
    db_tasks = result.scalars().all()
    return {"reminders": [Task.from_attributes(t) for t in db_tasks]}

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)