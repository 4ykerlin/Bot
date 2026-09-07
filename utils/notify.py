from aiogram import Bot
from config import TOKEN
from database import get_managers
import logging

bot = Bot(token=TOKEN)

async def notify_user(user_id: int, text: str):
    try:
        await bot.send_message(user_id, text)
    except Exception as e:
        logging.error(f"Не удалось уведомить {user_id}: {e}")

async def notify_managers(text: str):
    managers = await get_managers()
    for mgr in managers:
        await notify_user(mgr[0], text)