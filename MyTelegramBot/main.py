import asyncio
import logging
from aiogram import Bot, Dispatcher
from config import TOKEN
from database import init_db
from handlers import user, manager, admin

async def main():
    await init_db()
    bot = Bot(token=TOKEN)
    dp = Dispatcher()
    dp.include_router(user.router)
    dp.include_router(manager.router)
    dp.include_router(admin.router)
    await dp.start_polling(bot)

if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    asyncio.run(main())