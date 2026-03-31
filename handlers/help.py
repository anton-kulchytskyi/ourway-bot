from aiogram import Router
from aiogram.filters import Command
from aiogram.types import Message

router = Router()


@router.message(Command("help"))
async def cmd_help(message: Message) -> None:
    await message.answer(
        "<b>OurWay Bot — Commands</b>\n\n"
        "📋 <b>Tasks</b>\n"
        "/add &lt;title&gt; — add a new task\n"
        "/my — show your active tasks\n"
        "/done &lt;id&gt; — mark task as done\n\n"
        "📅 <b>Day</b>\n"
        "/today — your plan for today\n"
        "/tonight — plan tomorrow (evening ritual)\n\n"
        "ℹ️ <b>Other</b>\n"
        "/start — log in or register\n"
        "/help — show this message",
        parse_mode="HTML",
    )
