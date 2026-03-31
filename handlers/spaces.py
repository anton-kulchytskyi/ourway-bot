"""
Space management: /spaces, create space FSM
"""
import logging

from aiogram import F, Router
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from aiogram.types import CallbackQuery, InlineKeyboardButton, InlineKeyboardMarkup, Message

from services import api_client

logger = logging.getLogger(__name__)
router = Router()


class CreateSpaceStates(StatesGroup):
    waiting_for_name = State()
    waiting_for_emoji = State()


# ── /spaces ───────────────────────────────────────────────────────────────────

@router.message(Command("spaces"))
async def cmd_spaces(message: Message) -> None:
    telegram_id = message.from_user.id
    if not await api_client.ensure_token(telegram_id):
        await message.answer("Please send /start first to log in.")
        return

    spaces = await api_client.get_spaces(telegram_id)
    if spaces is None:
        await message.answer("❌ Failed to load spaces.")
        return

    keyboard = InlineKeyboardMarkup(inline_keyboard=[[
        InlineKeyboardButton(text="➕ Create new space", callback_data="create_space"),
    ]])

    if not spaces:
        await message.answer(
            "You don't have any spaces yet.\n\nCreate your first one:",
            reply_markup=keyboard,
        )
        return

    lines = ["<b>Your spaces:</b>", ""]
    for s in spaces:
        emoji = s.get("emoji") or "📁"
        lines.append(f"{emoji} {s['name']}")

    await message.answer(
        "\n".join(lines),
        parse_mode="HTML",
        reply_markup=keyboard,
    )


# ── Create space flow ─────────────────────────────────────────────────────────

@router.callback_query(F.data == "create_space")
async def cb_create_space(callback: CallbackQuery, state: FSMContext) -> None:
    await callback.answer()
    await state.set_state(CreateSpaceStates.waiting_for_name)
    await callback.message.answer("📁 What's the name for your new space?\n(e.g. Family, Home, Work)")


@router.message(CreateSpaceStates.waiting_for_name, F.text)
async def process_space_name(message: Message, state: FSMContext) -> None:
    name = message.text.strip()
    if len(name) < 2:
        await message.answer("Please enter at least 2 characters.")
        return

    await state.update_data(space_name=name)
    await state.set_state(CreateSpaceStates.waiting_for_emoji)

    keyboard = InlineKeyboardMarkup(inline_keyboard=[[
        InlineKeyboardButton(text="Skip", callback_data="space_emoji_skip"),
    ]])
    await message.answer(
        f"Got it: <b>{name}</b>\n\nSend an emoji for this space (or skip):",
        parse_mode="HTML",
        reply_markup=keyboard,
    )


@router.callback_query(F.data == "space_emoji_skip")
async def cb_skip_emoji(callback: CallbackQuery, state: FSMContext) -> None:
    await callback.answer()
    data = await state.get_data()
    await _finish_create_space(callback.message, state, callback.from_user.id, data["space_name"], None)


@router.message(CreateSpaceStates.waiting_for_emoji, F.text)
async def process_space_emoji(message: Message, state: FSMContext) -> None:
    emoji = message.text.strip()
    data = await state.get_data()
    await _finish_create_space(message, state, message.from_user.id, data["space_name"], emoji)


async def _finish_create_space(
    message: Message, state: FSMContext,
    telegram_id: int, name: str, emoji: str | None,
) -> None:
    space = await api_client.create_space(telegram_id, name, emoji)
    await state.clear()
    if space:
        icon = space.get("emoji") or "📁"
        await message.answer(
            f"✅ Space created: {icon} <b>{space['name']}</b>\n\n"
            "Now you can add tasks with /add",
            parse_mode="HTML",
        )
    else:
        await message.answer("❌ Failed to create space. Please try again.")
