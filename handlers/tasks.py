"""
Task commands: /add, /my, /done
"""
import logging

from aiogram import F, Router
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from aiogram.types import CallbackQuery, InlineKeyboardButton, InlineKeyboardMarkup, Message

from handlers.scheduling_helpers import day_keyboard, due_keyboard, parse_due_date, resolve_due, resolve_scheduled
from locales import t
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
    waiting_for_day = State()
    waiting_for_due = State()
    waiting_for_due_input = State()


# ── /add ─────────────────────────────────────────────────────────────────────

@router.message(Command("add"))
async def cmd_add(message: Message, state: FSMContext) -> None:
    telegram_id = message.from_user.id
    if not await api_client.ensure_token(telegram_id):
        await message.answer(t("common.not_logged_in", api_client.get_locale(telegram_id)))
        return

    args = message.text.split(maxsplit=1)[1].strip() if " " in message.text else ""

    if args:
        await _pick_space_or_create(message, state, telegram_id, args)
    else:
        await state.set_state(AddTaskStates.waiting_for_title)
        await message.answer(t("task.title_prompt", api_client.get_locale(telegram_id)))


@router.message(AddTaskStates.waiting_for_title, F.text)
async def process_task_title(message: Message, state: FSMContext) -> None:
    title = message.text.strip()
    telegram_id = message.from_user.id
    locale = api_client.get_locale(telegram_id)
    if len(title) < 2:
        await message.answer(t("common.min_2_chars", locale))
        return
    await _pick_space_or_create(message, state, telegram_id, title)


async def _pick_space_or_create(
    message: Message, state: FSMContext, telegram_id: int, title: str
) -> None:
    locale = api_client.get_locale(telegram_id)
    spaces = await api_client.get_spaces(telegram_id)
    if not spaces:
        await state.clear()
        keyboard = InlineKeyboardMarkup(inline_keyboard=[[
            InlineKeyboardButton(
                text=t("task.create_space_btn", locale),
                callback_data="create_space",
            ),
        ]])
        await message.answer(t("task.no_spaces", locale), reply_markup=keyboard)
        return

    if len(spaces) == 1:
        await _ask_day(message, state, telegram_id, title, spaces[0]["id"], spaces[0]["name"])
        return

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
        t("task.pick_space", locale, title=title),
        reply_markup=InlineKeyboardMarkup(inline_keyboard=buttons),
        parse_mode="HTML",
    )


@router.callback_query(AddTaskStates.waiting_for_space, F.data.startswith("space:"))
async def process_space_pick(callback: CallbackQuery, state: FSMContext) -> None:
    _, space_id, space_name = callback.data.split(":", 2)
    data = await state.get_data()
    title = data.get("task_title", "")
    await callback.message.delete()
    await _ask_day(callback.message, state, callback.from_user.id, title, int(space_id), space_name)
    await callback.answer()


async def _ask_day(
    message: Message, state: FSMContext,
    telegram_id: int, title: str, space_id: int, space_name: str,
) -> None:
    locale = api_client.get_locale(telegram_id)
    await state.update_data(task_title=title, space_id=space_id, space_name=space_name)
    await state.set_state(AddTaskStates.waiting_for_day)
    await message.answer(t("sched.pick_day", locale), reply_markup=day_keyboard(locale, "task_day"))


@router.callback_query(AddTaskStates.waiting_for_day, F.data.startswith("task_day:"))
async def process_day_pick(callback: CallbackQuery, state: FSMContext) -> None:
    value = callback.data.split(":", 1)[1]
    telegram_id = callback.from_user.id
    locale = api_client.get_locale(telegram_id)

    scheduled_date = resolve_scheduled(value)
    await state.update_data(scheduled_date=scheduled_date)
    await callback.message.delete()
    await state.set_state(AddTaskStates.waiting_for_due)
    await callback.message.answer(
        t("sched.due_prompt", locale),
        reply_markup=due_keyboard(locale, has_scheduled=scheduled_date is not None, prefix="task_due"),
    )
    await callback.answer()


@router.callback_query(AddTaskStates.waiting_for_due, F.data.startswith("task_due:"))
async def process_due_pick(callback: CallbackQuery, state: FSMContext) -> None:
    value = callback.data.split(":", 1)[1]
    telegram_id = callback.from_user.id
    locale = api_client.get_locale(telegram_id)

    if value == "enter":
        await callback.message.delete()
        await state.set_state(AddTaskStates.waiting_for_due_input)
        await callback.message.answer(t("sched.due_enter_hint", locale))
        await callback.answer()
        return

    data = await state.get_data()
    due_date = resolve_due(value, data.get("scheduled_date"))
    await callback.message.delete()
    await _create_task_final(callback.message, state, telegram_id, data, due_date)
    await callback.answer()


@router.message(AddTaskStates.waiting_for_due_input, F.text)
async def process_due_input(message: Message, state: FSMContext) -> None:
    telegram_id = message.from_user.id
    locale = api_client.get_locale(telegram_id)
    due_date = parse_due_date(message.text)
    if due_date is None:
        await message.answer(t("sched.due_invalid", locale))
        return

    data = await state.get_data()
    await _create_task_final(message, state, telegram_id, data, due_date)


async def _create_task_final(
    message: Message, state: FSMContext,
    telegram_id: int, data: dict, due_date: str | None,
) -> None:
    locale = api_client.get_locale(telegram_id)
    title = data["task_title"]
    space_id = data["space_id"]
    space_name = data["space_name"]
    scheduled_date = data.get("scheduled_date")

    task = await api_client.create_task(
        telegram_id, title, space_id,
        scheduled_date=scheduled_date,
        due_date=due_date,
    )
    await state.clear()
    if task:
        await message.answer(
            t("task.created", locale, title=title, space=space_name, id=str(task["id"])),
            parse_mode="HTML",
        )
    else:
        await message.answer(t("task.create_failed", locale))


# ── /my ──────────────────────────────────────────────────────────────────────

@router.message(Command("my"))
async def cmd_my(message: Message) -> None:
    telegram_id = message.from_user.id
    if not await api_client.ensure_token(telegram_id):
        await message.answer(t("common.not_logged_in", api_client.get_locale(telegram_id)))
        return

    locale = api_client.get_locale(telegram_id)
    tasks = await api_client.get_my_tasks(telegram_id)
    if tasks is None:
        await message.answer(t("task.load_failed", locale))
        return

    active = [t_ for t_ in tasks if t_["status"] != "done"]
    if not active:
        await message.answer(t("task.no_active", locale))
        return

    lines = [t("task.list_header", locale), ""]
    for task in active:
        emoji = STATUS_EMOJI.get(task["status"], "•")
        lines.append(f"{emoji} #{task['id']} {task['title']}")

    lines += ["", t("task.list_footer", locale)]
    await message.answer("\n".join(lines), parse_mode="HTML")


# ── /done ─────────────────────────────────────────────────────────────────────

@router.message(Command("done"))
async def cmd_done(message: Message) -> None:
    telegram_id = message.from_user.id
    if not await api_client.ensure_token(telegram_id):
        await message.answer(t("common.not_logged_in", api_client.get_locale(telegram_id)))
        return

    locale = api_client.get_locale(telegram_id)
    args = message.text.split(maxsplit=1)[1].strip() if " " in message.text else ""
    if not args or not args.isdigit():
        await message.answer(t("task.done_usage", locale))
        return

    task_id = int(args)
    result = await api_client.complete_task(telegram_id, task_id)
    if result:
        await message.answer(t("task.done_success", locale, id=str(task_id)))
    else:
        await message.answer(t("task.done_failed", locale, id=str(task_id)))
