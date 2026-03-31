import asyncio
import logging
import os

from aiogram import Bot, Dispatcher
from aiogram.filters import CommandStart
from aiogram.types import Message

from config import BOT_TOKEN

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


async def main():
    bot = Bot(token=BOT_TOKEN)
    dp = Dispatcher()

    @dp.message(CommandStart())
    async def start(message: Message):
        await message.answer(
            f"👋 Привіт, {message.from_user.first_name}!\n\nЯ OurWay бот. Поки що в розробці."
        )

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
