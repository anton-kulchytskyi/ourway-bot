"""
Daily plan commands: /today, /tonight (evening ritual)
"""
import logging
from datetime import date, timedelta

from aiogram import F, Router
from aiogram.filters import Command
from aiogram.types import CallbackQuery, InlineKeyboardButton, InlineKeyboardMarkup, Message

from services import api_client

logger = logging.getLogger(__name__)
router = Router()


def _fmt_time(t: str | None) -> str:
    """'07:30:00' → '07:30'"""
    if not t:
        return ""
    return t[:5]


def _format_day_view(day: dict, title: str) -> str:
    lines = [f"<b>{title}</b>", ""]

    schedule = day.get("schedule_items", [])
    events = day.get("events", [])
    tasks = day.get("tasks", [])

    if schedule:
        for item in schedule:
            t = _fmt_time(item.get("time_start"))
            lines.append(f"🕐 {t} {item['title']}")

    if events:
        for event in events:
            t = _fmt_time(event.get("time_start"))
            prefix = f" {t}" if t else ""
            lines.append(f"📅{prefix} {event['title']}")

    if tasks:
        for task in tasks:
            t = _fmt_time(task.get("time_start"))
            prefix = f" {t}" if t else ""
            status = task.get("status", "")
            emoji = "✅" if status == "done" else "📝"
            lines.append(f"{emoji}{prefix} {task['title']}")

    if not (schedule or events or tasks):
        lines.append("Nothing planned yet.")

    plan = day.get("plan", {})
    if plan.get("status") == "confirmed":
        lines += ["", "✅ Plan confirmed"]

    return "\n".join(lines)


# ── /today ────────────────────────────────────────────────────────────────────

@router.message(Command("today"))
async def cmd_today(message: Message) -> None:
    telegram_id = message.from_user.id
    if not await api_client.ensure_token(telegram_id):
        await message.answer("Please send /start first to log in.")
        return

    today = date.today().isoformat()
    day = await api_client.get_day(telegram_id, today)
    if day is None:
        await message.answer("❌ Could not load today's plan.")
        return

    text = _format_day_view(day, f"☀️ Today — {today}")
    await message.answer(text, parse_mode="HTML")


# ── /tonight (evening ritual) ─────────────────────────────────────────────────

@router.message(Command("tonight"))
async def cmd_tonight(message: Message) -> None:
    telegram_id = message.from_user.id
    if not await api_client.ensure_token(telegram_id):
        await message.answer("Please send /start first to log in.")
        return

    tomorrow = (date.today() + timedelta(days=1)).isoformat()
    day = await api_client.get_day(telegram_id, tomorrow)
    if day is None:
        await message.answer("❌ Could not load tomorrow's plan.")
        return

    text = _format_day_view(day, f"🌙 Tomorrow — {tomorrow}")

    plan = day.get("plan", {})
    if plan.get("status") == "confirmed":
        await message.answer(text + "\n\n✅ Already confirmed!", parse_mode="HTML")
        return

    keyboard = InlineKeyboardMarkup(inline_keyboard=[[
        InlineKeyboardButton(
            text="✅ Confirm plan",
            callback_data=f"confirm_day:{tomorrow}",
        ),
        InlineKeyboardButton(
            text="➕ Add task",
            callback_data="add_task_from_ritual",
        ),
    ]])
    await message.answer(text, parse_mode="HTML", reply_markup=keyboard)


# ── Callbacks from /tonight and evening ritual notification ───────────────────

@router.callback_query(F.data.startswith("confirm_day:"))
async def cb_confirm_day(callback: CallbackQuery) -> None:
    telegram_id = callback.from_user.id
    if not await api_client.ensure_token(telegram_id):
        await callback.answer("Please /start first.", show_alert=True)
        return

    date_str = callback.data.split(":", 1)[1]
    result = await api_client.confirm_day(telegram_id, date_str)
    if result:
        await callback.message.edit_reply_markup(reply_markup=None)
        await callback.message.answer("✅ Plan confirmed! Sleep well 🌙")
    else:
        await callback.answer("❌ Could not confirm. Try again.", show_alert=True)
    await callback.answer()


@router.callback_query(F.data == "add_task_from_ritual")
async def cb_add_task_ritual(callback: CallbackQuery) -> None:
    await callback.answer()
    await callback.message.answer(
        "Use /add &lt;task title&gt; to add a task.\n"
        "Then come back and confirm the plan.",
        parse_mode="HTML",
    )


# ── Handler for evening ritual deep link: /start ritual ───────────────────────

@router.message(Command("tonight"))
async def ritual_reminder(message: Message) -> None:
    """Alias — same as /tonight."""
    await cmd_tonight(message)
