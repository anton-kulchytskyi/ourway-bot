"""
Task commands: /add, /my, /done
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

STATUS_EMOJI = {
    "backlog": "📋",
    "todo": "📝",
    "in_progress": "🔄",
    "blocked": "🚫",
    "done": "✅",
}


class AddTaskStates(StatesGroup):
    waiting_for_title = State()
    waiting_for_space = State()


def _require_login(telegram_id: int) -> bool:
    return api_client.get_token(telegram_id) is None


# ── /add ─────────────────────────────────────────────────────────────────────

@router.message(Command("add"))
async def cmd_add(message: Message, state: FSMContext) -> None:
    telegram_id = message.from_user.id
    if _require_login(telegram_id):
        await message.answer("Please send /start first to log in.")
        return

    # Title can be provided inline: /add Buy groceries
    args = message.text.split(maxsplit=1)[1].strip() if " " in message.text else ""

    if args:
        await _pick_space_or_create(message, state, telegram_id, args)
    else:
        await state.set_state(AddTaskStates.waiting_for_title)
        await message.answer("📝 What's the task title?")


@router.message(AddTaskStates.waiting_for_title, F.text)
async def process_task_title(message: Message, state: FSMContext) -> None:
    title = message.text.strip()
    if len(title) < 2:
        await message.answer("Please enter at least 2 characters.")
        return
    await _pick_space_or_create(message, state, message.from_user.id, title)


async def _pick_space_or_create(
    message: Message, state: FSMContext, telegram_id: int, title: str
) -> None:
    spaces = await api_client.get_spaces(telegram_id)
    if not spaces:
        await state.clear()
        keyboard = InlineKeyboardMarkup(inline_keyboard=[[
            InlineKeyboardButton(text="➕ Create a space", callback_data="create_space"),
        ]])
        await message.answer(
            "You don't have any spaces yet.\nCreate one first:",
            reply_markup=keyboard,
        )
        return

    if len(spaces) == 1:
        await _create_task(message, state, telegram_id, title, spaces[0]["id"], spaces[0]["name"])
        return

    # Multiple spaces — ask which one
    await state.update_data(task_title=title)
    await state.set_state(AddTaskStates.waiting_for_space)

    buttons = [
        [InlineKeyboardButton(
            text=f"{s.get('emoji', '📁')} {s['name']}",
            callback_data=f"space:{s['id']}:{s['name']}"
        )]
        for s in spaces
    ]
    await message.answer(
        f"📝 <b>{title}</b>\n\nWhich space should this go to?",
        reply_markup=InlineKeyboardMarkup(inline_keyboard=buttons),
        parse_mode="HTML",
    )


@router.callback_query(AddTaskStates.waiting_for_space, F.data.startswith("space:"))
async def process_space_pick(callback: CallbackQuery, state: FSMContext) -> None:
    _, space_id, space_name = callback.data.split(":", 2)
    data = await state.get_data()
    title = data.get("task_title", "")
    await callback.message.delete()
    await _create_task(callback.message, state, callback.from_user.id, title, int(space_id), space_name)
    await callback.answer()


async def _create_task(
    message: Message, state: FSMContext,
    telegram_id: int, title: str, space_id: int, space_name: str
) -> None:
    task = await api_client.create_task(telegram_id, title, space_id)
    await state.clear()
    if task:
        await message.answer(
            f"✅ Task added!\n"
            f"<b>{title}</b> → {space_name}\n"
            f"ID: #{task['id']}",
            parse_mode="HTML",
        )
    else:
        await message.answer("❌ Failed to create task. Please try again.")


# ── /my ──────────────────────────────────────────────────────────────────────

@router.message(Command("my"))
async def cmd_my(message: Message) -> None:
    telegram_id = message.from_user.id
    if _require_login(telegram_id):
        await message.answer("Please send /start first to log in.")
        return

    tasks = await api_client.get_my_tasks(telegram_id)
    if tasks is None:
        await message.answer("❌ Failed to load tasks.")
        return

    active = [t for t in tasks if t["status"] != "done"]
    if not active:
        await message.answer("🎉 No active tasks! You're all caught up.")
        return

    lines = ["<b>Your tasks:</b>", ""]
    for t in active:
        emoji = STATUS_EMOJI.get(t["status"], "•")
        lines.append(f"{emoji} #{t['id']} {t['title']}")

    lines += ["", "Use /done &lt;id&gt; to complete a task."]
    await message.answer("\n".join(lines), parse_mode="HTML")


# ── /done ─────────────────────────────────────────────────────────────────────

@router.message(Command("done"))
async def cmd_done(message: Message) -> None:
    telegram_id = message.from_user.id
    if _require_login(telegram_id):
        await message.answer("Please send /start first to log in.")
        return

    args = message.text.split(maxsplit=1)[1].strip() if " " in message.text else ""
    if not args or not args.isdigit():
        await message.answer("Usage: /done <task_id>\nExample: /done 42")
        return

    task_id = int(args)
    result = await api_client.complete_task(telegram_id, task_id)
    if result:
        await message.answer(f"✅ Task #{task_id} marked as done!")
    else:
        await message.answer(f"❌ Could not complete task #{task_id}. Check the ID and try again.")
