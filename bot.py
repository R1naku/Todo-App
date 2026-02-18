# bot.py
import asyncio
import os
from aiogram import Bot, Dispatcher
from dotenv import load_dotenv

from handlers.start import router as start_router  # твой роутер /start

load_dotenv()
BOT_TOKEN = os.getenv("BOT_TOKEN")

bot = Bot(token=BOT_TOKEN)
dp = Dispatcher()

# Подключаем роутеры
dp.include_router(start_router)

async def main():
    print("Бот запущен...")
    await dp.start_polling(bot, allowed_updates=["message"])

if __name__ == "__main__":
    asyncio.run(main())