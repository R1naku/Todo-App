import os
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from aiogram import Bot
from aiogram.types import UserProfilePhotos
from dotenv import load_dotenv
from database import get_db
from models import TelegramUser
from schemas import TelegramUserOut

router = APIRouter(prefix="/tg", tags=["telegram"])

load_dotenv()

BOT_TOKEN = os.getenv("BOT_TOKEN")

bot = Bot(token=BOT_TOKEN)

async def get_bot() -> Bot:
    return bot

@router.get("/info/{identifier}", response_model=TelegramUserOut)
async def get_telegram_info(
    identifier: str,
    db: AsyncSession = Depends(get_db),
    bot: Bot = Depends(get_bot)
):
    try:
        chat = await bot.get_chat(identifier)
        photos: UserProfilePhotos = await bot.get_user_profile_photos(chat.id, limit=1)
        avatar_url = None
        if photos.total_count > 0:
            biggest = photos.photos[0][-1]
            file = await bot.get_file(biggest.file_id)
            save_path = f"static/avatars/{chat.id}.jpg"
            await bot.download_file(file.file_path, save_path)
            avatar_url = f"/static/avatars/{chat.id}.jpg"

    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=" Telegram-User не найден или бот его не видел"
        )

    stmt = select(TelegramUser).where(TelegramUser.id == chat.id)
    result = await db.execute(stmt)
    tg_user = result.scalar_one_or_none()

    if tg_user:
        tg_user.username = chat.username
        tg_user.first_name = chat.first_name
        tg_user.last_name = chat.last_name
        tg_user.avatar_url = avatar_url
    else:
        tg_user = TelegramUser(
            id=chat.id,
            username=chat.username,
            first_name=chat.first_name,
            last_name=chat.last_name,
            avatar_url=avatar_url,
        )
        db.add(tg_user)

    await db.commit()
    await db.refresh(tg_user)

    return tg_user