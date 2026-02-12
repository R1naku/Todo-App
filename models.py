from datetime import datetime
from typing import List, Optional
from pydantic import BaseModel
from sqlalchemy import Column, Integer, String, DateTime, ARRAY
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

    class Config:
        from_attributes = True

class ShareTask(BaseModel):
    user_id: int