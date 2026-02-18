# handlers/start.py
from aiogram import Router
from aiogram.filters import CommandStart
from aiogram.types import Message
from sqlalchemy import select

from database import async_session
from models import TelegramUser  # Добавьте этот импорт!

router = Router(name="start")


@router.message(CommandStart())
async def cmd_start(message: Message):
    user = message.from_user

    async with async_session() as session:
        async with session.begin():
            stmt = select(TelegramUser).where(TelegramUser.id == user.id)
            result = await session.execute(stmt)
            db_user = result.scalar_one_or_none()

            if db_user:
                db_user.username = user.username
                db_user.first_name = user.first_name
                db_user.last_name = user.last_name
                text = f"Рад тебя видеть снова, {user.first_name}! 👋\nДанные обновлены."
            else:
                new_user = TelegramUser(
                    id=user.id,
                    username=user.username,
                    first_name=user.first_name,
                    last_name=user.last_name,
                    avatar_url=None,
                )
                session.add(new_user)
                text = f"Привет, {user.first_name}! 🎉\nТы зарегистрирован в системе задач."

            await session.commit()

    await message.answer(text)