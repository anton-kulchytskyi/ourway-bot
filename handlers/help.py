from aiogram import Router
from aiogram.filters import Command
from aiogram.types import Message

from locales import t
from services import api_client

router = Router()


@router.message(Command("help"))
async def cmd_help(message: Message) -> None:
    locale = api_client.get_locale(message.from_user.id)
    await message.answer(t("help.text", locale), parse_mode="HTML")
