import asyncio
import logging
import os

from aiogram import Bot, Dispatcher
from aiogram.fsm.storage.memory import MemoryStorage

from config import BOT_TOKEN
from handlers import auth, tasks, help, daily, spaces, kids, add_child

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


async def main():
    bot = Bot(token=BOT_TOKEN)
    dp = Dispatcher(storage=MemoryStorage())

    dp.include_router(auth.router)
    dp.include_router(spaces.router)
    dp.include_router(tasks.router)
    dp.include_router(kids.router)
    dp.include_router(add_child.router)
    dp.include_router(daily.router)
    dp.include_router(help.router)

    # Brief delay so Railway can stop the previous instance before we start polling.
    # Without this, rolling deploy causes a TelegramConflictError for ~1s.
    startup_delay = int(os.getenv("STARTUP_DELAY_SECONDS", "4"))
    if startup_delay:
        logger.info("Waiting %ds before polling (rolling deploy guard)...", startup_delay)
        await asyncio.sleep(startup_delay)

    logger.info("Bot started")
    await dp.start_polling(bot, drop_pending_updates=True)


if __name__ == "__main__":
    asyncio.run(main())
