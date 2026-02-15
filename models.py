from datetime import datetime
from typing import List, Optional
from pydantic import BaseModel, ConfigDict
from sqlalchemy import Column, Integer, String, DateTime, ARRAY, func
from sqlalchemy.orm import Mapped, mapped_column
from database import Base

class DBTask(Base):
    __tablename__ = "tasks"

    id = Column(Integer, primary_key=True, index=True)
    title = Column(String, nullable=False)
    description = Column(String)
    due_date = Column(DateTime)
    priority = Column(String)
    owner_id = Column(Integer, nullable=False)
    shared_with = Column(ARRAY(Integer), default=[])
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

class TaskBase(BaseModel):
    title: str
    description: Optional[str] = None
    due_date: Optional[datetime] = None

class TaskCreate(TaskBase):
    pass

class TaskUpdate(BaseModel):
    title: Optional[str] = None
    description: Optional[str] = None
    priority: Optional[str] = None
    due_date: Optional[datetime] = None

class TaskAnalysis(BaseModel):
    advice: str
    suggested_priority: str

class Task(TaskBase):
    id: int
    owner_id: int
    priority: Optional[str] = None
    shared_with: List[int] = []
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)

class ShareTask(BaseModel):
    user_id: int

class TelegramUser(Base):
    __tablename__ = "telegram_users"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    username: Mapped[str | None] = mapped_column(String(100), unique=True)
    first_name: Mapped[str] = mapped_column(String(100))
    last_name: Mapped[str | None] = mapped_column(String(100))
    avatar_url: Mapped[str | None] = mapped_column(String(500))
    updated_at: Mapped[datetime] = mapped_column(
        DateTime, server_default=func.now(), onupdate=func.now()
    )