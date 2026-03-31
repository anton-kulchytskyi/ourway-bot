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

from services import api_client

logger = logging.getLogger(__name__)
router = Router()


class AddChildFSM(StatesGroup):
    name = State()
    autonomy = State()
    has_tg = State()


def _autonomy_kb() -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(inline_keyboard=[
        [
            InlineKeyboardButton(text="1 — Supervised (≤12)", callback_data="aut:1"),
        ],
        [
            InlineKeyboardButton(text="2 — Semi (12–14)", callback_data="aut:2"),
        ],
        [
            InlineKeyboardButton(text="3 — Autonomous (14+)", callback_data="aut:3"),
        ],
        [InlineKeyboardButton(text="❌ Cancel", callback_data="aut:cancel")],
    ])


def _has_tg_kb() -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(inline_keyboard=[
        [
            InlineKeyboardButton(text="✅ Yes — send invite link", callback_data="hastg:yes"),
            InlineKeyboardButton(text="🚫 No — I manage for them", callback_data="hastg:no"),
        ],
        [InlineKeyboardButton(text="❌ Cancel", callback_data="hastg:cancel")],
    ])


@router.message(Command("add_child"))
async def cmd_add_child(message: Message, state: FSMContext) -> None:
    telegram_id = message.from_user.id
    if not await api_client.ensure_token(telegram_id):
        await message.answer("Please send /start first to log in.")
        return

    await state.set_state(AddChildFSM.name)
    await message.answer("👶 What is the child's name?")


@router.message(AddChildFSM.name)
async def got_name(message: Message, state: FSMContext) -> None:
    name = message.text.strip() if message.text else ""
    if not name:
        await message.answer("Please enter a valid name.")
        return

    await state.update_data(name=name)
    await state.set_state(AddChildFSM.autonomy)
    await message.answer(
        f"Got it — <b>{name}</b>.\n\nChoose the autonomy level:",
        reply_markup=_autonomy_kb(),
        parse_mode="HTML",
    )


@router.callback_query(AddChildFSM.autonomy, F.data.startswith("aut:"))
async def got_autonomy(callback: CallbackQuery, state: FSMContext) -> None:
    value = callback.data.split(":")[1]
    await callback.message.delete()

    if value == "cancel":
        await state.clear()
        await callback.message.answer("Cancelled.")
        return

    await state.update_data(autonomy_level=int(value))
    await state.set_state(AddChildFSM.has_tg)
    await callback.message.answer(
        "Does the child have a Telegram account?",
        reply_markup=_has_tg_kb(),
    )


@router.callback_query(AddChildFSM.has_tg, F.data.startswith("hastg:"))
async def got_has_tg(callback: CallbackQuery, state: FSMContext) -> None:
    value = callback.data.split(":")[1]
    await callback.message.delete()

    if value == "cancel":
        await state.clear()
        await callback.message.answer("Cancelled.")
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
        await callback.message.answer("❌ Failed to create child profile. Please try again.")
        return

    child = result.get("child", {})
    invite_link = result.get("invite_link")
    name = child.get("name", data["name"])

    if is_managed:
        await callback.message.answer(
            f"✅ <b>{name}</b>'s profile created (managed).\n\n"
            "You can see their tasks in /kids and mark tasks done on their behalf.",
            parse_mode="HTML",
        )
    else:
        await callback.message.answer(
            f"✅ <b>{name}</b>'s account created.\n\n"
            f"Share this link with your child so they can connect their Telegram:\n\n"
            f"<code>{invite_link}</code>\n\n"
            "The link is valid for 24 hours.",
            parse_mode="HTML",
        )
