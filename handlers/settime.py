"""
/settime — change morning briefing or evening ritual time.

Flow:
  /settime → current times + [🌅 Morning] [🌙 Evening] buttons
  tap → "Enter new time (HH:MM):" prompt  (FSM)
  user sends "08:00" → validate → PATCH /users/me → confirm
"""
import logging
import re

from aiogram import F, Router
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from aiogram.types import CallbackQuery, InlineKeyboardButton, InlineKeyboardMarkup, Message

from locales import t
from services import api_client

logger = logging.getLogger(__name__)
router = Router()

_TIME_RE = re.compile(r"^([01]\d|2[0-3]):([0-5]\d)$")


class SetTimeFSM(StatesGroup):
    waiting_for_time = State()


def _settime_keyboard(locale: str) -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(inline_keyboard=[
        [
            InlineKeyboardButton(text=t("settime.morning_btn", locale), callback_data="settime:morning"),
            InlineKeyboardButton(text=t("settime.evening_btn", locale), callback_data="settime:evening"),
        ],
        [InlineKeyboardButton(text=t("settime.cancel_btn", locale), callback_data="settime:cancel")],
    ])


@router.message(Command("settime"))
async def cmd_settime(message: Message) -> None:
    telegram_id = message.from_user.id
    if not await api_client.ensure_token(telegram_id):
        await message.answer(t("common.not_logged_in", api_client.get_locale(telegram_id)))
        return

    locale = api_client.get_locale(telegram_id)
    me = await api_client.get_me(telegram_id)
    morning = me.get("morning_brief_time", "07:30") if me else "07:30"
    evening = me.get("evening_ritual_time", "21:00") if me else "21:00"

    await message.answer(
        t("settime.current", locale, morning=morning, evening=evening),
        parse_mode="HTML",
        reply_markup=_settime_keyboard(locale),
    )


@router.callback_query(F.data.startswith("settime:"))
async def settime_pick(callback: CallbackQuery, state: FSMContext) -> None:
    value = callback.data[len("settime:"):]
    locale = api_client.get_locale(callback.from_user.id)
    await callback.message.delete()

    if value == "cancel":
        await callback.answer()
        await callback.message.answer(t("common.cancelled", locale))
        return

    await state.update_data(settime_type=value)
    await state.set_state(SetTimeFSM.waiting_for_time)
    label = t("settime.morning_btn", locale) if value == "morning" else t("settime.evening_btn", locale)
    await callback.message.answer(t("settime.enter_time", locale, which=label))
    await callback.answer()


@router.message(SetTimeFSM.waiting_for_time, F.text)
async def settime_input(message: Message, state: FSMContext) -> None:
    telegram_id = message.from_user.id
    locale = api_client.get_locale(telegram_id)
    raw = (message.text or "").strip()

    if not _TIME_RE.match(raw):
        await message.answer(t("settime.invalid_format", locale))
        return

    data = await state.get_data()
    which = data.get("settime_type", "morning")
    await state.clear()

    field = "morning_brief_time" if which == "morning" else "evening_ritual_time"
    result = await api_client.update_me(telegram_id, **{field: raw})
    if result is None:
        await message.answer(t("settime.save_failed", locale))
        return

    label = t("settime.morning_btn", locale) if which == "morning" else t("settime.evening_btn", locale)
    await message.answer(t("settime.saved", locale, which=label, time=raw))
