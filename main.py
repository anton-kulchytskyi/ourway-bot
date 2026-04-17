import asyncio
import logging
import os

from aiogram import Bot, Dispatcher
from aiogram.fsm.storage.memory import MemoryStorage
from aiogram.types import BotCommand

from config import BOT_TOKEN
from handlers import auth, tasks, help, daily, spaces, kids, add_child, plan, schedule_mgmt, invite, timezone, events, settime

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


async def main():
    bot = Bot(token=BOT_TOKEN)
    dp = Dispatcher(storage=MemoryStorage())

    dp.include_router(auth.router)
    dp.include_router(spaces.router)
    dp.include_router(tasks.router)
    dp.include_router(plan.router)
    dp.include_router(schedule_mgmt.router)
    dp.include_router(kids.router)
    dp.include_router(add_child.router)
    dp.include_router(invite.router)
    dp.include_router(timezone.router)
    dp.include_router(settime.router)
    dp.include_router(events.router)
    dp.include_router(daily.router)
    dp.include_router(help.router)

    # Brief delay so Railway can stop the previous instance before we start polling.
    # Without this, rolling deploy causes a TelegramConflictError for ~1s.
    startup_delay = int(os.getenv("STARTUP_DELAY_SECONDS", "4"))
    if startup_delay:
        logger.info("Waiting %ds before polling (rolling deploy guard)...", startup_delay)
        await asyncio.sleep(startup_delay)

    await bot.set_my_commands([
        BotCommand(command="today",     description="My day plan"),
        BotCommand(command="my",        description="My active tasks"),
        BotCommand(command="add",       description="Add a task"),
        BotCommand(command="tonight",   description="Plan tomorrow (evening ritual)"),
        BotCommand(command="schedule",  description="View/manage schedule"),
        BotCommand(command="done",      description="Mark task as done"),
        BotCommand(command="plan",      description="Schedule a task from backlog"),
        BotCommand(command="events",    description="Upcoming events"),
        BotCommand(command="add_event", description="Add an event"),
        BotCommand(command="kids",      description="Children's tasks"),
        BotCommand(command="add_child", description="Add a child account"),
        BotCommand(command="spaces",    description="My spaces"),
        BotCommand(command="timezone",  description="View/change timezone"),
        BotCommand(command="settime",   description="Change briefing times"),
        BotCommand(command="web",       description="Open OurWay web app"),
        BotCommand(command="help",      description="Help"),
        BotCommand(command="start",     description="Start / login"),
    ])
    logger.info("Bot started")
    await dp.start_polling(bot, drop_pending_updates=True)


if __name__ == "__main__":
    asyncio.run(main())
