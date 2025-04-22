import asyncio
import logging
from aiogram import Bot, Dispatcher
from dotenv import load_dotenv

import db
from handlers.start_handler import router_reg

load_dotenv()
TOKEN = os.getenv('TOKEN')

bot = Bot(token=TOKEN)
dp = Dispatcher()


async def main():
    logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO)
    db.init_db()

    dp.include_routers(router_reg)

    await dp.start_polling(bot)

if __name__ == '__main__':
    asyncio.run(main())