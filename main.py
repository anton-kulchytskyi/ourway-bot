import asyncio
import logging

from aiogram import Bot, Dispatcher

from config import BOT_TOKEN

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


async def main():
    bot = Bot(token=BOT_TOKEN)
    dp = Dispatcher()

    logger.info("Bot started")
    await dp.start_polling(bot)


if __name__ == "__main__":
    asyncio.run(main())
