"""
Daily plan commands: /today, /tonight (evening ritual)
"""
import logging
from datetime import date, datetime, timedelta

from aiogram import F, Router
from aiogram.filters import Command
from aiogram.types import CallbackQuery, InlineKeyboardButton, InlineKeyboardMarkup, Message

from locales import t
from services import api_client

logger = logging.getLogger(__name__)
router = Router()

# Status → list of (new_status, locale_key) for transition buttons
_STATUS_TRANSITIONS: dict[str, list[tuple[str, str]]] = {
    "backlog":     [("todo", "daily.to_todo")],
    "todo":        [("in_progress", "daily.to_in_progress"), ("blocked", "daily.to_blocked")],
    "in_progress": [("todo", "daily.to_todo"), ("blocked", "daily.to_blocked"), ("done", "daily.to_done")],
    "blocked":     [("todo", "daily.to_todo"), ("in_progress", "daily.to_in_progress"), ("done", "daily.to_done")],
}


def _fmt_time(time_str) -> str:
    return str(time_str)[:5] if time_str else ""


def _parse_date(val) -> date | None:
    if not val:
        return None
    try:
        return datetime.strptime(str(val)[:10], "%Y-%m-%d").date()
    except ValueError:
        return None


def _format_day_view(day: dict, title: str, locale: str) -> str:
    """Simple day view for /today."""
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
            emoji = "✅" if task.get("status") == "done" else "📝"
            lines.append(f"{emoji}{prefix} {task['title']}")
    if not (schedule or events or tasks):
        lines.append(t("daily.nothing_planned", locale))
    if day.get("plan", {}).get("status") == "confirmed":
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


# ── /tonight ──────────────────────────────────────────────────────────────────

@router.message(Command("tonight"))
async def cmd_tonight(message: Message) -> None:
    telegram_id = message.from_user.id
    if not await api_client.ensure_token(telegram_id):
        await message.answer(t("common.not_logged_in", api_client.get_locale(telegram_id)))
        return
    locale = api_client.get_locale(telegram_id)
    role = api_client.get_role(telegram_id) or "member"
    tomorrow = (date.today() + timedelta(days=1)).isoformat()
    text, keyboard = await _build_tonight_view(telegram_id, tomorrow, locale, role)
    await message.answer(text, parse_mode="HTML", reply_markup=keyboard)


async def _build_tonight_view(
    telegram_id: int,
    tomorrow: str,
    locale: str,
    role: str,
) -> tuple[str, InlineKeyboardMarkup | None]:
    today = date.today()
    tomorrow_date = today + timedelta(days=1)
    backlog_cutoff = today + timedelta(days=7)

    day = await api_client.get_day(telegram_id, tomorrow)
    if day is None:
        return t("daily.load_tomorrow_failed", locale), None

    all_tasks = await api_client.get_my_tasks(telegram_id) or []
    active = [tk for tk in all_tasks if tk.get("status") != "done"]

    in_progress = [tk for tk in active if tk.get("status") == "in_progress"]
    blocked_tasks = [tk for tk in active if tk.get("status") == "blocked"]
    todo = [tk for tk in active if tk.get("status") == "todo"]
    backlog = [
        tk for tk in active
        if tk.get("status") == "backlog"
        and (d := _parse_date(tk.get("due_date"))) is not None
        and d <= backlog_cutoff
    ]

    # Children data
    children_lines: list[str] = []
    if role in ("owner", "member"):
        family_day = await api_client.get_family_day(telegram_id, tomorrow) or []
        for member_day in family_day:
            if member_day.get("role") != "child":
                continue
            child_id = member_day["user_id"]
            child_name = member_day["user_name"]
            child_day_data = member_day.get("day", {})

            sched_parts = [
                f"{_fmt_time(s.get('time_start'))} {s['title']}".strip()
                for s in child_day_data.get("schedule_items", [])
            ]
            event_parts = [
                f"{_fmt_time(ev.get('time_start'))} {ev['title']}".strip()
                for ev in child_day_data.get("events", [])
            ]
            day_parts = sched_parts + [f"📅 {p}" for p in event_parts]
            day_str = ", ".join(day_parts) if day_parts else t("daily.nothing_planned", locale)

            child_tasks = await api_client.get_child_tasks(telegram_id, child_id) or []
            active_ct = [ct for ct in child_tasks if ct.get("status") != "done"]
            blocked_ct = sum(1 for ct in active_ct if ct.get("status") == "blocked")
            total_ct = len(active_ct)

            summary = ""
            if total_ct > 0:
                summary = f" · {t('daily.child_tasks_count', locale, n=total_ct)}"
                if blocked_ct > 0:
                    summary += f", {t('daily.child_blocked_count', locale, n=blocked_ct)}"
            children_lines.append(f"🧒 {child_name}: {day_str}{summary}")

    # Build message text
    lines: list[str] = [f"<b>{t('daily.tomorrow_title', locale, date=tomorrow)}</b>"]

    own_schedule = day.get("schedule_items", [])
    if own_schedule:
        lines += ["", f"<b>{t('daily.section_schedule', locale)}</b>"]
        for item in own_schedule:
            time = _fmt_time(item.get("time_start"))
            lines.append(f"🕐 {time} {item['title']}")

    if children_lines:
        lines += ["", f"<b>{t('daily.section_kids', locale)}</b>"]
        lines.extend(children_lines)

    own_events = day.get("events", [])
    if own_events:
        lines += ["", f"<b>{t('daily.section_events', locale)}</b>"]
        for ev in own_events:
            time = _fmt_time(ev.get("time_start"))
            prefix = f" {time}" if time else ""
            lines.append(f"📅{prefix} {ev['title']}")

    # Task sections with inline buttons
    keyboard_rows: list[list[InlineKeyboardButton]] = []

    def _add_task_group(group: list, section_label: str) -> None:
        if not group:
            return
        lines.append(f"\n{section_label}")
        for tk in group:
            task_id = tk["id"]
            title_ = tk["title"]
            task_status = tk.get("status", "backlog")
            due_d = _parse_date(tk.get("due_date"))
            extra = ""
            if due_d and due_d < today:
                extra = f" · {t('task.overdue_label', locale, days=(today - due_d).days)}"
            elif due_d and due_d <= tomorrow_date:
                extra = f" · {t('task.due_today_label', locale)}"
            lines.append(f"  · {title_}{extra}")
            short = title_[:28] + "…" if len(title_) > 28 else title_
            keyboard_rows.append([
                InlineKeyboardButton(
                    text=f"⚙️ {short}",
                    callback_data=f"ts:{task_id}:{task_status}",
                ),
                InlineKeyboardButton(
                    text="📅 →tmrw",
                    callback_data=f"tst:{task_id}",
                ),
            ])

    has_tasks = any([in_progress, blocked_tasks, todo, backlog])
    if has_tasks:
        lines += ["", f"<b>{t('daily.section_tasks', locale)}</b>"]
        _add_task_group(in_progress, t("daily.status_in_progress", locale))
        _add_task_group(blocked_tasks, t("daily.status_blocked", locale))
        _add_task_group(todo, t("daily.status_todo", locale))
        _add_task_group(backlog, t("daily.status_backlog", locale))
    else:
        lines += ["", t("daily.no_active_tasks", locale)]

    plan = day.get("plan", {})
    if plan.get("status") == "confirmed":
        lines += ["", t("daily.plan_confirmed", locale)]
        keyboard = InlineKeyboardMarkup(inline_keyboard=keyboard_rows) if keyboard_rows else None
    else:
        confirm_row = [
            InlineKeyboardButton(
                text=t("daily.confirm_btn", locale),
                callback_data=f"confirm_day:{tomorrow}",
            ),
            InlineKeyboardButton(
                text=t("daily.add_task_btn", locale),
                callback_data="add_task_from_ritual",
            ),
        ]
        keyboard = InlineKeyboardMarkup(inline_keyboard=[confirm_row] + keyboard_rows)

    return "\n".join(lines), keyboard


# ── Task status picker ─────────────────────────────────────────────────────────

@router.callback_query(F.data.startswith("ts:"))
async def cb_task_status_pick(callback: CallbackQuery) -> None:
    await callback.answer()
    telegram_id = callback.from_user.id
    locale = api_client.get_locale(telegram_id)
    _, task_id_str, current_status = callback.data.split(":", 2)
    task_id = int(task_id_str)

    transitions = _STATUS_TRANSITIONS.get(current_status, [])
    if not transitions:
        await callback.message.answer(t("daily.no_transitions", locale))
        return

    rows = [[
        InlineKeyboardButton(
            text=t(label_key, locale),
            callback_data=f"tss:{task_id}:{new_status}",
        )
    ] for new_status, label_key in transitions]

    await callback.message.answer(
        t("daily.pick_new_status", locale),
        reply_markup=InlineKeyboardMarkup(inline_keyboard=rows),
    )


@router.callback_query(F.data.startswith("tss:"))
async def cb_task_set_status(callback: CallbackQuery) -> None:
    await callback.answer()
    telegram_id = callback.from_user.id
    locale = api_client.get_locale(telegram_id)
    _, task_id_str, new_status = callback.data.split(":", 2)
    task_id = int(task_id_str)

    result = await api_client.update_task(telegram_id, task_id, status=new_status)
    if result:
        await callback.message.edit_reply_markup(reply_markup=None)
        status_label = t(f"daily.status_{new_status}", locale)
        await callback.message.answer(t("daily.status_updated", locale, status=status_label))
    else:
        await callback.message.answer(t("daily.update_failed", locale))


@router.callback_query(F.data.startswith("tst:"))
async def cb_task_schedule_tomorrow(callback: CallbackQuery) -> None:
    await callback.answer()
    telegram_id = callback.from_user.id
    locale = api_client.get_locale(telegram_id)
    _, task_id_str = callback.data.split(":", 1)
    task_id = int(task_id_str)
    tomorrow = (date.today() + timedelta(days=1)).isoformat()

    result = await api_client.update_task(telegram_id, task_id, scheduled_date=tomorrow)
    if result:
        await callback.message.answer(t("daily.scheduled_tomorrow", locale, date=tomorrow))
    else:
        await callback.message.answer(t("daily.update_failed", locale))


# ── Confirm day & add task callbacks ─────────────────────────────────────────

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
