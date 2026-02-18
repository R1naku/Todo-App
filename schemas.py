from datetime import datetime
from typing import Optional, List, Any

from pydantic import BaseModel, ConfigDict


class TelegramUserOut(BaseModel):
    id: int
    username: str | None = None
    first_name: str
    last_name: str | None = None
    avatar_url: str | None = None

    model_config = ConfigDict(from_attributes=True)


class PlanUpdate(BaseModel):
    title: Optional[str] = None
    # description: Optional[str] = None
    # color: Optional[str] = None
    # icon: Optional[str] = None  # и т.д. — добавляй по мере необходимости


class PlanCreate(BaseModel):
    title: str


class Plan(PlanCreate):
    id: int
    owner_id: int
    shared_with: List[int] = []
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)