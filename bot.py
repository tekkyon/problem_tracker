import asyncio
import logging
import subprocess

from aiogram import Bot, Dispatcher, F
from aiogram.fsm.state import State, StatesGroup
from aiogram.fsm.storage.memory import MemoryStorage

import handlers
from config import load_config, Config

DB = 'greenea_issues.db'

logger = logging.getLogger(__name__)

logging.basicConfig(level=logging.INFO)


async def main() -> None:
    config: Config = load_config()

    bot = Bot(token=config.tg_bot.token, parse_mode="HTML")

    storage = MemoryStorage()
    dp = Dispatcher(storage=storage)
    dp.include_router(handlers.router, )

    await bot.delete_webhook(drop_pending_updates=True)
    await dp.start_polling(bot)

if __name__ == '__main__':
    asyncio.run(main())
    # subprocess.run(['streamlit', 'run', r'dashboard.py'])
