"""
Shared helpers for scheduling flows used by both /add (tasks.py) and /plan (plan.py).

- resolve_scheduled / resolve_due   — pure date logic
- day_keyboard / due_keyboard       — inline keyboards (caller supplies callback prefix)
- parse_due_date                    — parses user-typed date string → ISO datetime or None
"""
from datetime import date, datetime, timedelta, timezone

from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup

from locales import t


def resolve_scheduled(value: str) -> str | None:
    """'today' | 'tomorrow' → ISO date string; anything else → None."""
    today = date.today()
    if value == "today":
        return today.isoformat()
    if value == "tomorrow":
        return (today + timedelta(days=1)).isoformat()
    return None


def resolve_due(value: str, scheduled_date: str | None) -> str | None:
    """'same' | 'plus3' | 'week' → ISO datetime string (end of day UTC); else → None."""
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


def parse_due_date(text: str) -> str | None:
    """Parse a user-typed ISO date string → end-of-day UTC ISO datetime, or None on error."""
    try:
        parsed = date.fromisoformat(text.strip())
        dt = datetime(parsed.year, parsed.month, parsed.day, 23, 59, 59, tzinfo=timezone.utc)
        return dt.isoformat()
    except ValueError:
        return None


def day_keyboard(locale: str, prefix: str) -> InlineKeyboardMarkup:
    """Inline keyboard for picking scheduled day. prefix e.g. 'task_day' or 'plan_day'."""
    return InlineKeyboardMarkup(inline_keyboard=[[
        InlineKeyboardButton(text=t("sched.today_btn", locale), callback_data=f"{prefix}:today"),
        InlineKeyboardButton(text=t("sched.tomorrow_btn", locale), callback_data=f"{prefix}:tomorrow"),
        InlineKeyboardButton(text=t("sched.no_date_btn", locale), callback_data=f"{prefix}:none"),
    ]])


def due_keyboard(locale: str, has_scheduled: bool, prefix: str) -> InlineKeyboardMarkup:
    """Inline keyboard for picking due date. prefix e.g. 'task_due' or 'plan_due'."""
    buttons = []
    if has_scheduled:
        buttons.append(InlineKeyboardButton(text=t("sched.due_same_btn", locale), callback_data=f"{prefix}:same"))
    buttons += [
        InlineKeyboardButton(text=t("sched.due_plus3_btn", locale), callback_data=f"{prefix}:plus3"),
        InlineKeyboardButton(text=t("sched.due_week_btn", locale), callback_data=f"{prefix}:week"),
    ]
    return InlineKeyboardMarkup(inline_keyboard=[
        buttons,
        [
            InlineKeyboardButton(text=t("sched.due_enter_btn", locale), callback_data=f"{prefix}:enter"),
            InlineKeyboardButton(text=t("sched.due_none_btn", locale), callback_data=f"{prefix}:none"),
        ],
    ])
