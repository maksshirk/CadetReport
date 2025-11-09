import asyncio
import logging
from handlers import router
from initializator import bot, scheduler
from aiogram import Dispatcher
from scheduler_jobs import go_report, go_report_komandir
from time import gmtime, strftime

# Включаем логирование, чтобы не пропустить важные сообщения
logging.basicConfig(level=logging.INFO)

async def main():
    # Объект бота
    # Диспетчер
    dp = Dispatcher()
    dp.include_router(router)
    scheduler.add_job(go_report_komandir, "cron", hour=22)
    scheduler.add_job(go_report, "cron", hour=21, minute=58)
    scheduler.add_job(go_report, "cron", hour=22, minute=15)
    scheduler.add_job(go_report, "cron", hour=22, minute=30)
    scheduler.add_job(go_report, "cron", hour=22, minute=45)
    scheduler.start()
    await dp.start_polling(bot)

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print(strftime("%Y-%m-%d %H:%M:%S", gmtime()) + " Бот выключен.")