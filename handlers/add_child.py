"""
/add_child — add a child to the family.

Two scenarios:
  1. Managed (no TG account) — parent controls everything on behalf of the child.
  2. With TG — generates a deep-link invite so the child can connect their account.
"""
import logging

from aiogram import F, Router
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from aiogram.types import (
    CallbackQuery,
    InlineKeyboardButton,
    InlineKeyboardMarkup,
    Message,
)

from locales import t
from services import api_client

logger = logging.getLogger(__name__)
router = Router()


class AddChildFSM(StatesGroup):
    name = State()
    autonomy = State()
    has_tg = State()


def _autonomy_kb(locale: str) -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text=t("add_child.autonomy_supervised", locale), callback_data="aut:1")],
        [InlineKeyboardButton(text=t("add_child.autonomy_semi", locale), callback_data="aut:2")],
        [InlineKeyboardButton(text=t("add_child.autonomy_autonomous", locale), callback_data="aut:3")],
        [InlineKeyboardButton(text=t("add_child.cancel_btn", locale), callback_data="aut:cancel")],
    ])


def _has_tg_kb(locale: str) -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(inline_keyboard=[
        [
            InlineKeyboardButton(text=t("add_child.has_tg_yes", locale), callback_data="hastg:yes"),
            InlineKeyboardButton(text=t("add_child.has_tg_no", locale), callback_data="hastg:no"),
        ],
        [InlineKeyboardButton(text=t("add_child.cancel_btn", locale), callback_data="hastg:cancel")],
    ])


@router.message(Command("add_child"))
async def cmd_add_child(message: Message, state: FSMContext) -> None:
    telegram_id = message.from_user.id
    if not await api_client.ensure_token(telegram_id):
        await message.answer(t("common.not_logged_in", api_client.get_locale(telegram_id)))
        return

    locale = api_client.get_locale(telegram_id)
    await state.set_state(AddChildFSM.name)
    await message.answer(t("add_child.name_prompt", locale))


@router.message(AddChildFSM.name)
async def got_name(message: Message, state: FSMContext) -> None:
    name = message.text.strip() if message.text else ""
    telegram_id = message.from_user.id
    locale = api_client.get_locale(telegram_id)

    if not name:
        await message.answer(t("add_child.invalid_name", locale))
        return

    await state.update_data(name=name)
    await state.set_state(AddChildFSM.autonomy)
    await message.answer(
        t("add_child.autonomy_prompt", locale, name=name),
        reply_markup=_autonomy_kb(locale),
        parse_mode="HTML",
    )


@router.callback_query(AddChildFSM.autonomy, F.data.startswith("aut:"))
async def got_autonomy(callback: CallbackQuery, state: FSMContext) -> None:
    value = callback.data.split(":")[1]
    locale = api_client.get_locale(callback.from_user.id)
    await callback.message.delete()

    if value == "cancel":
        await state.clear()
        await callback.message.answer(t("common.cancelled", locale))
        return

    await state.update_data(autonomy_level=int(value))
    await state.set_state(AddChildFSM.has_tg)
    await callback.message.answer(
        t("add_child.has_tg_prompt", locale),
        reply_markup=_has_tg_kb(locale),
    )


@router.callback_query(AddChildFSM.has_tg, F.data.startswith("hastg:"))
async def got_has_tg(callback: CallbackQuery, state: FSMContext) -> None:
    value = callback.data.split(":")[1]
    locale = api_client.get_locale(callback.from_user.id)
    await callback.message.delete()

    if value == "cancel":
        await state.clear()
        await callback.message.answer(t("common.cancelled", locale))
        return

    data = await state.get_data()
    await state.clear()

    telegram_id = callback.from_user.id
    is_managed = value == "no"

    result = await api_client.create_child_bot(
        telegram_id=telegram_id,
        name=data["name"],
        autonomy_level=data["autonomy_level"],
        is_managed=is_managed,
    )

    if result is None:
        await callback.message.answer(t("add_child.create_failed", locale))
        return

    child = result.get("child", {})
    invite_link = result.get("invite_link")
    name = child.get("name", data["name"])

    if is_managed:
        await callback.message.answer(
            t("add_child.managed_created", locale, name=name),
            parse_mode="HTML",
        )
    else:
        kb = InlineKeyboardMarkup(inline_keyboard=[
            [InlineKeyboardButton(
                text=t("add_child.tg_connect_btn", locale, name=name),
                url=invite_link or "",
            )]
        ])
        await callback.message.answer(
            t("add_child.tg_created", locale, name=name),
            parse_mode="HTML",
            reply_markup=kb,
        )
