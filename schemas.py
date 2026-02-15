from pydantic import BaseModel, ConfigDict

class TelegramUserOut(BaseModel):
    id: int
    username: str | None
    first_name: str
    last_name: str | None
    avatar_url: str | None

    model_config = ConfigDict(from_attributes=True)