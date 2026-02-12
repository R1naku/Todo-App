import os
from fastapi import Depends, HTTPException, status
from fastapi.security import APIKeyHeader
from telegram_init_data import validate, parse, TelegramInitDataError
from pydantic import BaseModel


class TelegramUser(BaseModel):
    id: int
    first_name: str | None = None
    last_name: str | None = None
    username: str | None = None
init_data_header = APIKeyHeader(name="X-Telegram-Init-Data", auto_error=False)


async def get_current_user(
    init_data_raw: str = Depends(init_data_header)
) -> TelegramUser:

    if not init_data_raw:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Telegram initData missing"
        )

    bot_token = os.getenv("BOT_TOKEN")
    if not bot_token:
        raise HTTPException(
            status_code=500,
            detail="BOT_TOKEN not configured in environment"
        )

    try:
        validate(
            value=init_data_raw,
            token=bot_token,
            expires_in=3600,
        )

        parsed = parse(init_data_raw)

        user_data = parsed.user
        if not user_data:
            raise ValueError("User data not found in initData")

        return TelegramUser(
            id=user_data.id,
            first_name=user_data.first_name,
            last_name=user_data.last_name,
            username=user_data.username,
        )

    except TelegramInitDataError as e:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=f"Invalid Telegram initData: {str(e)}"
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=f"Unexpected error during initData validation: {str(e)}"
        )