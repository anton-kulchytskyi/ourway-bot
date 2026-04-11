"""
/timezone — view and change the user's timezone.

Shows current timezone and a list of common IANA timezones as inline buttons.
"""
import logging

from aiogram import F, Router
from aiogram.filters import Command
from aiogram.types import CallbackQuery, InlineKeyboardButton, InlineKeyboardMarkup, Message

from locales import t
from services import api_client

logger = logging.getLogger(__name__)
router = Router()

# Common timezones shown as buttons, in pairs
TIMEZONE_ROWS = [
    ("UTC",             "Europe/London"),
    ("Europe/Dublin",   "Europe/Warsaw"),
    ("Europe/Kyiv",     "Europe/Berlin"),
    ("Europe/Paris",    "Europe/Rome"),
    ("Europe/Moscow",   "Europe/Istanbul"),
    ("America/New_York","America/Los_Angeles"),
    ("Asia/Dubai",      "Asia/Kolkata"),
    ("Asia/Singapore",  "Asia/Tokyo"),
]


def _tz_keyboard(locale: str) -> InlineKeyboardMarkup:
    rows = []
    for left, right in TIMEZONE_ROWS:
        rows.append([
            InlineKeyboardButton(text=left.split("/")[-1].replace("_", " "), callback_data=f"tz:{left}"),
            InlineKeyboardButton(text=right.split("/")[-1].replace("_", " "), callback_data=f"tz:{right}"),
        ])
    rows.append([InlineKeyboardButton(text=t("tz.cancel_btn", locale), callback_data="tz:cancel")])
    return InlineKeyboardMarkup(inline_keyboard=rows)


@router.message(Command("timezone"))
async def cmd_timezone(message: Message) -> None:
    telegram_id = message.from_user.id
    if not await api_client.ensure_token(telegram_id):
        await message.answer(t("common.not_logged_in", api_client.get_locale(telegram_id)))
        return

    locale = api_client.get_locale(telegram_id)
    me = await api_client.get_me(telegram_id)
    current_tz = me.get("timezone", "UTC") if me else "UTC"

    await message.answer(
        t("tz.current", locale, tz=current_tz),
        parse_mode="HTML",
        reply_markup=_tz_keyboard(locale),
    )


@router.callback_query(F.data.startswith("tz:"))
async def got_timezone(callback: CallbackQuery) -> None:
    value = callback.data[3:]  # strip "tz:"
    locale = api_client.get_locale(callback.from_user.id)
    await callback.message.delete()

    if value == "cancel":
        await callback.message.answer(t("common.cancelled", locale))
        return

    result = await api_client.update_me(callback.from_user.id, timezone=value)
    if result is None:
        await callback.message.answer(t("tz.save_failed", locale))
        return

    await callback.message.answer(t("tz.saved", locale, tz=value), parse_mode="HTML")
