import asyncio
import logging
from aiogram import Bot, Dispatcher
from dotenv import load_dotenv
import os


import db
from handlers.start_handler import router_reg
from handlers.profile import router_profile
from handlers.watch_forms import router_forms


load_dotenv()
TOKEN = os.getenv('TOKEN')

bot = Bot(token=TOKEN)
dp = Dispatcher()


async def main():
    logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO)

    await db.init_db()

    dp.include_routers(router_reg, router_profile, router_forms)

    await dp.start_polling(bot)

if __name__ == '__main__':
    asyncio.run(main())