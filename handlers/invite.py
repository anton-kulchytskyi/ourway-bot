"""
/invite — generate an organisation-level invite link.

One step: /invite → creates an org-level invitation → sends tappable buttons.
The recipient joins the organisation (appears in Family page).
Space access is managed separately by the owner.
"""
import logging

from aiogram import Router
from aiogram.filters import Command
from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup, Message

from config import FRONTEND_URL, BOT_USERNAME
from locales import t
from services import api_client

logger = logging.getLogger(__name__)
router = Router()


@router.message(Command("invite"))
async def cmd_invite(message: Message) -> None:
    telegram_id = message.from_user.id
    if not await api_client.ensure_token(telegram_id):
        await message.answer(t("common.not_logged_in", api_client.get_locale(telegram_id)))
        return

    locale = api_client.get_locale(telegram_id)

    result = await api_client.create_invitation(telegram_id)
    if result is None:
        await message.answer(t("invite.create_failed", locale))
        return

    token = result["token"]
    tg_link = f"https://t.me/{BOT_USERNAME}?start=inv_{token}"
    web_link = f"{FRONTEND_URL.rstrip('/')}/{locale}/invite/{token}"

    kb = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text=t("invite.open_tg_btn", locale), url=tg_link)],
        [InlineKeyboardButton(text=t("invite.open_web_btn", locale), url=web_link)],
    ])

    await message.answer(
        t("invite.created", locale),
        parse_mode="HTML",
        reply_markup=kb,
    )
