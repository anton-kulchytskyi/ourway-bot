"""
Daily plan commands: /today, /tonight (evening ritual)
"""
import logging
from datetime import date, timedelta

from aiogram import F, Router
from aiogram.filters import Command
from aiogram.types import CallbackQuery, InlineKeyboardButton, InlineKeyboardMarkup, Message

from locales import t
from services import api_client

logger = logging.getLogger(__name__)
router = Router()


def _fmt_time(time_str: str | None) -> str:
    """'07:30:00' → '07:30'"""
    if not time_str:
        return ""
    return time_str[:5]


def _format_day_view(day: dict, title: str, locale: str) -> str:
    lines = [f"<b>{title}</b>", ""]

    schedule = day.get("schedule_items", [])
    events = day.get("events", [])
    tasks = day.get("tasks", [])

    if schedule:
        for item in schedule:
            time = _fmt_time(item.get("time_start"))
            lines.append(f"🕐 {time} {item['title']}")

    if events:
        for event in events:
            time = _fmt_time(event.get("time_start"))
            prefix = f" {time}" if time else ""
            lines.append(f"📅{prefix} {event['title']}")

    if tasks:
        for task in tasks:
            time = _fmt_time(task.get("time_start"))
            prefix = f" {time}" if time else ""
            status = task.get("status", "")
            emoji = "✅" if status == "done" else "📝"
            lines.append(f"{emoji}{prefix} {task['title']}")

    if not (schedule or events or tasks):
        lines.append(t("daily.nothing_planned", locale))

    plan = day.get("plan", {})
    if plan.get("status") == "confirmed":
        lines += ["", t("daily.plan_confirmed", locale)]

    return "\n".join(lines)


# ── /today ────────────────────────────────────────────────────────────────────

@router.message(Command("today"))
async def cmd_today(message: Message) -> None:
    telegram_id = message.from_user.id
    if not await api_client.ensure_token(telegram_id):
        await message.answer(t("common.not_logged_in", api_client.get_locale(telegram_id)))
        return

    locale = api_client.get_locale(telegram_id)
    today = date.today().isoformat()
    day = await api_client.get_day(telegram_id, today)
    if day is None:
        await message.answer(t("daily.load_today_failed", locale))
        return

    text = _format_day_view(day, t("daily.today_title", locale, date=today), locale)
    await message.answer(text, parse_mode="HTML")


# ── /tonight (evening ritual) ─────────────────────────────────────────────────

@router.message(Command("tonight"))
async def cmd_tonight(message: Message) -> None:
    telegram_id = message.from_user.id
    if not await api_client.ensure_token(telegram_id):
        await message.answer(t("common.not_logged_in", api_client.get_locale(telegram_id)))
        return

    locale = api_client.get_locale(telegram_id)
    tomorrow = (date.today() + timedelta(days=1)).isoformat()
    day = await api_client.get_day(telegram_id, tomorrow)
    if day is None:
        await message.answer(t("daily.load_tomorrow_failed", locale))
        return

    text = _format_day_view(day, t("daily.tomorrow_title", locale, date=tomorrow), locale)

    plan = day.get("plan", {})
    if plan.get("status") == "confirmed":
        await message.answer(
            text + "\n\n" + t("daily.already_confirmed", locale),
            parse_mode="HTML",
        )
        return

    keyboard = InlineKeyboardMarkup(inline_keyboard=[[
        InlineKeyboardButton(
            text=t("daily.confirm_btn", locale),
            callback_data=f"confirm_day:{tomorrow}",
        ),
        InlineKeyboardButton(
            text=t("daily.add_task_btn", locale),
            callback_data="add_task_from_ritual",
        ),
    ]])
    await message.answer(text, parse_mode="HTML", reply_markup=keyboard)


# ── Callbacks from /tonight and evening ritual notification ───────────────────

@router.callback_query(F.data.startswith("confirm_day:"))
async def cb_confirm_day(callback: CallbackQuery) -> None:
    telegram_id = callback.from_user.id
    if not await api_client.ensure_token(telegram_id):
        await callback.answer(
            t("common.not_logged_in", api_client.get_locale(telegram_id)),
            show_alert=True,
        )
        return

    locale = api_client.get_locale(telegram_id)
    date_str = callback.data.split(":", 1)[1]
    result = await api_client.confirm_day(telegram_id, date_str)
    if result:
        await callback.message.edit_reply_markup(reply_markup=None)
        await callback.message.answer(t("daily.plan_confirmed_msg", locale))
    else:
        await callback.answer(t("daily.confirm_failed", locale), show_alert=True)
    await callback.answer()


@router.callback_query(F.data == "add_task_from_ritual")
async def cb_add_task_ritual(callback: CallbackQuery) -> None:
    await callback.answer()
    locale = api_client.get_locale(callback.from_user.id)
    await callback.message.answer(
        t("daily.add_task_hint", locale),
        parse_mode="HTML",
    )
