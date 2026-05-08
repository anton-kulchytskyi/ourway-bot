"""
Shared helpers for scheduling flows used by both /add (tasks.py) and /plan (plan.py).

- resolve_scheduled / resolve_due   — pure date logic
- day_keyboard / due_keyboard       — inline keyboards (caller supplies callback prefix)
- parse_due_date                    — parses user-typed date string → ISO datetime or None
- time_hour_keyboard                — two-step time picker: step 1 (hours)
- time_minute_keyboard              — two-step time picker: step 2 (minutes)
- parse_event_date                  — parses DD.MM / DD.MM.YYYY / YYYY-MM-DD → date
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


# ── Two-step time picker ───────────────────────────────────────────────────────

_HOURS = list(range(5, 23))  # 05..22


def time_hour_keyboard(locale: str, prefix: str, skip_data: str | None = None) -> InlineKeyboardMarkup:
    """Hour picker (step 1). prefix is the callback prefix, e.g. 'ev_th' or 'sch_tsh'.
    Buttons: {prefix}:{hour}  (hours 05-22, 4 per row).
    Optional skip row at the bottom if skip_data provided.
    """
    rows = []
    for i in range(0, len(_HOURS), 4):
        rows.append([
            InlineKeyboardButton(text=f"{h:02d}:__", callback_data=f"{prefix}:{h}")
            for h in _HOURS[i:i + 4]
        ])
    if skip_data:
        rows.append([InlineKeyboardButton(text=t("time.skip_btn", locale), callback_data=skip_data)])
    return InlineKeyboardMarkup(inline_keyboard=rows)


def time_minute_keyboard(
    hour: int,
    locale: str,
    prefix: str,
    back_prefix: str,
    skip_data: str | None = None,
) -> InlineKeyboardMarkup:
    """Minute picker (step 2): 00, 15, 30, 45 + Back row.
    prefix: callback prefix for minute selection, e.g. 'ev_tm' → {prefix}:{hour}:{minute}.
    back_prefix: callback prefix used for back button → {back_prefix}:back.
    """
    rows = [
        [
            InlineKeyboardButton(text=f"{hour:02d}:{m:02d}", callback_data=f"{prefix}:{hour}:{m}")
            for m in (0, 15, 30, 45)
        ],
        [InlineKeyboardButton(text=t("time.back_btn", locale), callback_data=f"{back_prefix}:back")],
    ]
    if skip_data:
        rows[-1].append(InlineKeyboardButton(text=t("time.skip_btn", locale), callback_data=skip_data))
    return InlineKeyboardMarkup(inline_keyboard=rows)


def parse_event_date(text: str) -> date | None:
    """Parse a date from user input: DD.MM, DD.MM.YYYY, or YYYY-MM-DD.
    For DD.MM: if the resulting date is in the past, advances to next year.
    Returns None on any parse error.
    """
    text = text.strip()
    today = date.today()

    # ISO format YYYY-MM-DD
    try:
        return date.fromisoformat(text)
    except ValueError:
        pass

    # European format with dots or slashes
    parts = text.replace("/", ".").split(".")
    if len(parts) == 2:
        try:
            day, month = int(parts[0]), int(parts[1])
            d = date(today.year, month, day)
            if d < today:
                d = date(today.year + 1, month, day)
            return d
        except ValueError:
            return None
    if len(parts) == 3:
        try:
            day, month, year = int(parts[0]), int(parts[1]), int(parts[2])
            if year < 100:
                year += 2000
            return date(year, month, day)
        except ValueError:
            return None

    return None
