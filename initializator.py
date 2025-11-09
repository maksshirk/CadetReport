from aiogram import Bot
from settings import TG_TOKEN
from apscheduler.schedulers.asyncio import AsyncIOScheduler

scheduler = AsyncIOScheduler()

bot = Bot(token=TG_TOKEN)