"""
/plan — schedule existing tasks (set scheduled_date + due_date).

Usage:
  /plan       → shows unscheduled tasks, pick one
  /plan 42    → schedule task #42 directly
"""
import logging
from datetime import date, datetime, timedelta, timezone

from aiogram import F, Router
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from aiogram.types import CallbackQuery, InlineKeyboardButton, InlineKeyboardMarkup, Message

from locales import t
from services import api_client

logger = logging.getLogger(__name__)
router = Router()


class PlanStates(StatesGroup):
    waiting_for_day = State()
    waiting_for_due = State()
    waiting_for_due_input = State()


def _day_keyboard(locale: str) -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(inline_keyboard=[[
        InlineKeyboardButton(text=t("sched.today_btn", locale), callback_data="plan_day:today"),
        InlineKeyboardButton(text=t("sched.tomorrow_btn", locale), callback_data="plan_day:tomorrow"),
        InlineKeyboardButton(text=t("sched.no_date_btn", locale), callback_data="plan_day:none"),
    ]])


def _due_keyboard(locale: str, has_scheduled: bool) -> InlineKeyboardMarkup:
    buttons = []
    if has_scheduled:
        buttons.append(InlineKeyboardButton(text=t("sched.due_same_btn", locale), callback_data="plan_due:same"))
    buttons += [
        InlineKeyboardButton(text=t("sched.due_plus3_btn", locale), callback_data="plan_due:plus3"),
        InlineKeyboardButton(text=t("sched.due_week_btn", locale), callback_data="plan_due:week"),
    ]
    return InlineKeyboardMarkup(inline_keyboard=[
        buttons,
        [
            InlineKeyboardButton(text=t("sched.due_enter_btn", locale), callback_data="plan_due:enter"),
            InlineKeyboardButton(text=t("sched.due_none_btn", locale), callback_data="plan_due:none"),
        ],
    ])


def _resolve_scheduled(value: str) -> str | None:
    today = date.today()
    if value == "today":
        return today.isoformat()
    if value == "tomorrow":
        return (today + timedelta(days=1)).isoformat()
    return None


def _resolve_due(value: str, scheduled_date: str | None) -> str | None:
    today = date.today()
    base = date.fromisoformat(scheduled_date) if scheduled_date else today
    if value == "same":
        target = base
    elif value == "plus3":
        target = today + timedelta(days=3)
    elif value == "week":
        target = today + timedelta(weeks=1)
    else:
        return None
    dt = datetime(target.year, target.month, target.day, 23, 59, 59, tzinfo=timezone.utc)
    return dt.isoformat()


# ── /plan ────────────────────────────────────────────────────────────────────

@router.message(Command("plan"))
async def cmd_plan(message: Message, state: FSMContext) -> None:
    telegram_id = message.from_user.id
    if not await api_client.ensure_token(telegram_id):
        await message.answer(t("common.not_logged_in", api_client.get_locale(telegram_id)))
        return

    locale = api_client.get_locale(telegram_id)
    args = message.text.split(maxsplit=1)[1].strip() if " " in message.text else ""

    if args:
        if not args.isdigit():
            await message.answer(t("sched.plan_usage", locale))
            return
        task_id = int(args)
        await _start_plan_flow(message, state, telegram_id, task_id)
        return

    # No args — show list of unscheduled tasks
    tasks = await api_client.get_my_tasks(telegram_id)
    if tasks is None:
        await message.answer(t("task.load_failed", locale))
        return

    unscheduled = [
        task for task in tasks
        if task.get("status") != "done" and not task.get("scheduled_date")
    ]
    if not unscheduled:
        await message.answer(t("sched.plan_empty", locale))
        return

    buttons = [
        [InlineKeyboardButton(
            text=f"#{task['id']} {task['title']}",
            callback_data=f"plan_pick:{task['id']}",
        )]
        for task in unscheduled
    ]
    await message.answer(
        t("sched.plan_pick", locale),
        reply_markup=InlineKeyboardMarkup(inline_keyboard=buttons),
    )


@router.callback_query(F.data.startswith("plan_pick:"))
async def cb_plan_pick(callback: CallbackQuery, state: FSMContext) -> None:
    task_id = int(callback.data.split(":", 1)[1])
    await callback.message.delete()
    await _start_plan_flow(callback.message, state, callback.from_user.id, task_id)
    await callback.answer()


async def _start_plan_flow(
    message: Message, state: FSMContext, telegram_id: int, task_id: int
) -> None:
    locale = api_client.get_locale(telegram_id)
    # Verify task exists and is accessible
    tasks = await api_client.get_my_tasks(telegram_id)
    if tasks is None:
        await message.answer(t("task.load_failed", locale))
        return
    task = next((task for task in tasks if task["id"] == task_id), None)
    if not task:
        await message.answer(t("sched.task_not_found", locale))
        return

    await state.update_data(plan_task_id=task_id, plan_task_title=task["title"])
    await state.set_state(PlanStates.waiting_for_day)
    await message.answer(t("sched.pick_day", locale), reply_markup=_day_keyboard(locale))


@router.callback_query(PlanStates.waiting_for_day, F.data.startswith("plan_day:"))
async def process_plan_day(callback: CallbackQuery, state: FSMContext) -> None:
    value = callback.data.split(":", 1)[1]
    telegram_id = callback.from_user.id
    locale = api_client.get_locale(telegram_id)

    scheduled_date = _resolve_scheduled(value)
    await state.update_data(plan_scheduled_date=scheduled_date)
    await callback.message.delete()
    await state.set_state(PlanStates.waiting_for_due)
    await callback.message.answer(
        t("sched.due_prompt", locale),
        reply_markup=_due_keyboard(locale, has_scheduled=scheduled_date is not None),
    )
    await callback.answer()


@router.callback_query(PlanStates.waiting_for_due, F.data.startswith("plan_due:"))
async def process_plan_due(callback: CallbackQuery, state: FSMContext) -> None:
    value = callback.data.split(":", 1)[1]
    telegram_id = callback.from_user.id
    locale = api_client.get_locale(telegram_id)

    if value == "enter":
        await callback.message.delete()
        await state.set_state(PlanStates.waiting_for_due_input)
        await callback.message.answer(t("sched.due_enter_hint", locale))
        await callback.answer()
        return

    data = await state.get_data()
    due_date = _resolve_due(value, data.get("plan_scheduled_date"))
    await callback.message.delete()
    await _apply_plan(callback.message, state, telegram_id, data, due_date)
    await callback.answer()


@router.message(PlanStates.waiting_for_due_input, F.text)
async def process_plan_due_input(message: Message, state: FSMContext) -> None:
    telegram_id = message.from_user.id
    locale = api_client.get_locale(telegram_id)
    try:
        parsed = date.fromisoformat(message.text.strip())
        dt = datetime(parsed.year, parsed.month, parsed.day, 23, 59, 59, tzinfo=timezone.utc)
        due_date = dt.isoformat()
    except ValueError:
        await message.answer(t("sched.due_invalid", locale))
        return

    data = await state.get_data()
    await _apply_plan(message, state, telegram_id, data, due_date)


async def _apply_plan(
    message: Message, state: FSMContext,
    telegram_id: int, data: dict, due_date: str | None,
) -> None:
    locale = api_client.get_locale(telegram_id)
    task_id = data["plan_task_id"]
    title = data["plan_task_title"]
    scheduled_date = data.get("plan_scheduled_date")

    fields: dict = {}
    if scheduled_date:
        fields["scheduled_date"] = scheduled_date
    if due_date:
        fields["due_date"] = due_date

    result = await api_client.update_task(telegram_id, task_id, **fields)
    await state.clear()

    if result:
        display_date = scheduled_date or "—"
        await message.answer(
            t("sched.plan_updated", locale, title=title, date=display_date),
            parse_mode="HTML",
        )
    else:
        await message.answer(t("task.create_failed", locale))
