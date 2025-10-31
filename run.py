import asyncio, settings, datetime, pymongo
from datetime import datetime
import logging
from aiogram import Bot, Dispatcher, types
from aiogram.filters.command import Command
from aiogram.types import Message
from aiogram.filters import CommandStart
from handlers import router
from settings import TG_TOKEN, MONGODB_LINK

# Включаем логирование, чтобы не пропустить важные сообщения
logging.basicConfig(level=logging.INFO)

# Запуск процесса поллинга новых апдейтов
async def main():
    # Объект бота
    bot = Bot(token=TG_TOKEN)
    # Диспетчер
    dp = Dispatcher()
    dp.include_router(router)
    await dp.start_polling(bot)

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("Бот выключен.")