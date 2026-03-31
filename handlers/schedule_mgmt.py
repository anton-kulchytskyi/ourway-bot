"""
/schedule — manage recurring schedule (школа, секції, робота).

Flow:
  /schedule → list + [➕ Add] [🗑 Delete]
  Add FSM: title → toggle weekdays → time_start → time_end → valid_from → valid_until
"""
import logging
from datetime import date

from aiogram import F, Router
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from aiogram.types import CallbackQuery, InlineKeyboardButton, InlineKeyboardMarkup, Message

from locales import t
from services import api_client

logger = logging.getLogger(__name__)
router = Router()

# Weekday number → locale key mapping (Mon=1 … Sun=7)
_DAY_KEYS = {
    1: "sch.days_mon",
    2: "sch.days_tue",
    3: "sch.days_wed",
    4: "sch.days_thu",
    5: "sch.days_fri",
    6: "sch.days_sat",
    7: "sch.days_sun",
}


class ScheduleAddFSM(StatesGroup):
    name = State()
    weekdays = State()
    time_start = State()
    time_end = State()
    valid_from = State()
    valid_until = State()


# ── Helpers ───────────────────────────────────────────────────────────────────

def _days_label(weekdays: list[int], locale: str) -> str:
    return ", ".join(t(_DAY_KEYS[d], locale) for d in sorted(weekdays))


def _weekday_keyboard(selected: set[int], locale: str) -> InlineKeyboardMarkup:
    """Toggle keyboard for weekdays. Selected days show ✅ prefix."""
    rows = []
    row = []
    for day_num, key in _DAY_KEYS.items():
        label = t(key, locale)
        prefix = "✅ " if day_num in selected else ""
        row.append(InlineKeyboardButton(
            text=f"{prefix}{label}",
            callback_data=f"sch_day:{day_num}",
        ))
        if len(row) == 4:  # 4 per row
            rows.append(row)
            row = []
    if row:
        rows.append(row)
    rows.append([InlineKeyboardButton(
        text=t("sch.days_done_btn", locale),
        callback_data="sch_day:done",
    )])
    return InlineKeyboardMarkup(inline_keyboard=rows)


def _fmt_schedule(s: dict, locale: str) -> str:
    days = _days_label(s.get("weekdays", []), locale)
    time_start = (s.get("time_start") or "")[:5]
    time_end = (s.get("time_end") or "")[:5]
    time_str = f"{time_start}–{time_end}" if time_end else time_start
    valid_until = s.get("valid_until")
    until_str = f" (до {valid_until})" if valid_until else ""
    return f"🕐 {s['title']} — {days}, {time_str}{until_str}"


# ── /schedule ─────────────────────────────────────────────────────────────────

@router.message(Command("schedule"))
async def cmd_schedule(message: Message) -> None:
    telegram_id = message.from_user.id
    if not await api_client.ensure_token(telegram_id):
        await message.answer(t("common.not_logged_in", api_client.get_locale(telegram_id)))
        return

    locale = api_client.get_locale(telegram_id)
    schedules = await api_client.get_schedules(telegram_id)

    keyboard = InlineKeyboardMarkup(inline_keyboard=[[
        InlineKeyboardButton(text=t("sch.add_btn", locale), callback_data="sch_action:add"),
        InlineKeyboardButton(text=t("sch.delete_btn", locale), callback_data="sch_action:delete"),
    ]])

    if not schedules:
        await message.answer(t("sch.list_empty", locale), reply_markup=keyboard)
        return

    lines = [t("sch.list_header", locale), ""]
    for s in schedules:
        lines.append(_fmt_schedule(s, locale))

    await message.answer("\n".join(lines), parse_mode="HTML", reply_markup=keyboard)


# ── Action callbacks ──────────────────────────────────────────────────────────

@router.callback_query(F.data == "sch_action:add")
async def cb_add(callback: CallbackQuery, state: FSMContext) -> None:
    await callback.answer()
    locale = api_client.get_locale(callback.from_user.id)
    await state.set_state(ScheduleAddFSM.name)
    await callback.message.answer(t("sch.name_prompt", locale))


@router.callback_query(F.data == "sch_action:delete")
async def cb_delete_list(callback: CallbackQuery) -> None:
    await callback.answer()
    telegram_id = callback.from_user.id
    locale = api_client.get_locale(telegram_id)

    schedules = await api_client.get_schedules(telegram_id)
    if not schedules:
        await callback.message.answer(t("sch.list_empty", locale))
        return

    buttons = [
        [InlineKeyboardButton(
            text=f"{s['title']} ({_days_label(s.get('weekdays', []), locale)})",
            callback_data=f"sch_del:{s['id']}:{s['title']}",
        )]
        for s in schedules
    ]
    await callback.message.answer(
        t("sch.pick_to_delete", locale),
        reply_markup=InlineKeyboardMarkup(inline_keyboard=buttons),
    )


@router.callback_query(F.data.startswith("sch_del:"))
async def cb_confirm_delete(callback: CallbackQuery) -> None:
    _, schedule_id, title = callback.data.split(":", 2)
    telegram_id = callback.from_user.id
    locale = api_client.get_locale(telegram_id)
    await callback.message.delete()

    ok = await api_client.delete_schedule(telegram_id, int(schedule_id))
    if ok:
        await callback.message.answer(t("sch.deleted", locale, title=title), parse_mode="HTML")
    else:
        await callback.message.answer(t("sch.delete_failed", locale))
    await callback.answer()


# ── Add FSM ───────────────────────────────────────────────────────────────────

@router.message(ScheduleAddFSM.name, F.text)
async def fsm_name(message: Message, state: FSMContext) -> None:
    name = message.text.strip()
    telegram_id = message.from_user.id
    locale = api_client.get_locale(telegram_id)

    if len(name) < 2:
        await message.answer(t("common.min_2_chars", locale))
        return

    await state.update_data(sch_name=name, sch_days=[])
    await state.set_state(ScheduleAddFSM.weekdays)
    await message.answer(
        t("sch.days_prompt", locale),
        reply_markup=_weekday_keyboard(set(), locale),
    )


@router.callback_query(ScheduleAddFSM.weekdays, F.data.startswith("sch_day:"))
async def fsm_toggle_day(callback: CallbackQuery, state: FSMContext) -> None:
    value = callback.data.split(":", 1)[1]
    telegram_id = callback.from_user.id
    locale = api_client.get_locale(telegram_id)
    data = await state.get_data()
    # Store as list (JSON-serialisable); work with set for toggle logic
    selected: set[int] = set(data.get("sch_days", []))

    if value == "done":
        if not selected:
            await callback.answer(t("sch.days_none_selected", locale), show_alert=True)
            return
        await callback.message.delete()
        await state.update_data(sch_days=sorted(selected))
        await state.set_state(ScheduleAddFSM.time_start)
        await callback.message.answer(t("sch.time_start_prompt", locale))
        await callback.answer()
        return

    day_num = int(value)
    if day_num in selected:
        selected.discard(day_num)
    else:
        selected.add(day_num)

    await state.update_data(sch_days=sorted(selected))
    # Edit the keyboard in-place to reflect toggle
    await callback.message.edit_reply_markup(
        reply_markup=_weekday_keyboard(selected, locale)
    )
    await callback.answer()


@router.message(ScheduleAddFSM.time_start, F.text)
async def fsm_time_start(message: Message, state: FSMContext) -> None:
    telegram_id = message.from_user.id
    locale = api_client.get_locale(telegram_id)
    time_str = message.text.strip()

    if not _valid_time(time_str):
        await message.answer(t("sch.time_invalid", locale))
        return

    await state.update_data(sch_time_start=_normalise_time(time_str))
    await state.set_state(ScheduleAddFSM.time_end)
    keyboard = InlineKeyboardMarkup(inline_keyboard=[[
        InlineKeyboardButton(text=t("sch.time_skip_btn", locale), callback_data="sch_time_end:skip"),
    ]])
    await message.answer(t("sch.time_end_prompt", locale), reply_markup=keyboard)


@router.callback_query(ScheduleAddFSM.time_end, F.data == "sch_time_end:skip")
async def fsm_time_end_skip(callback: CallbackQuery, state: FSMContext) -> None:
    await callback.answer()
    await state.update_data(sch_time_end=None)
    await callback.message.delete()
    await _ask_valid_from(callback.message, state, callback.from_user.id)


@router.message(ScheduleAddFSM.time_end, F.text)
async def fsm_time_end(message: Message, state: FSMContext) -> None:
    telegram_id = message.from_user.id
    locale = api_client.get_locale(telegram_id)
    time_str = message.text.strip()

    if not _valid_time(time_str):
        await message.answer(t("sch.time_invalid", locale))
        return

    await state.update_data(sch_time_end=_normalise_time(time_str))
    await _ask_valid_from(message, state, telegram_id)


async def _ask_valid_from(message: Message, state: FSMContext, telegram_id: int) -> None:
    locale = api_client.get_locale(telegram_id)
    await state.set_state(ScheduleAddFSM.valid_from)
    keyboard = InlineKeyboardMarkup(inline_keyboard=[[
        InlineKeyboardButton(
            text=t("sch.valid_from_today_btn", locale),
            callback_data="sch_valid_from:today",
        ),
    ]])
    await message.answer(t("sch.valid_from_prompt", locale), reply_markup=keyboard)


@router.callback_query(ScheduleAddFSM.valid_from, F.data == "sch_valid_from:today")
async def fsm_valid_from_today(callback: CallbackQuery, state: FSMContext) -> None:
    await callback.answer()
    await state.update_data(sch_valid_from=date.today().isoformat())
    await callback.message.delete()
    await _ask_valid_until(callback.message, state, callback.from_user.id)


@router.message(ScheduleAddFSM.valid_from, F.text)
async def fsm_valid_from(message: Message, state: FSMContext) -> None:
    telegram_id = message.from_user.id
    locale = api_client.get_locale(telegram_id)
    try:
        parsed = date.fromisoformat(message.text.strip())
        await state.update_data(sch_valid_from=parsed.isoformat())
    except ValueError:
        await message.answer(t("sch.date_invalid", locale))
        return
    await _ask_valid_until(message, state, telegram_id)


async def _ask_valid_until(message: Message, state: FSMContext, telegram_id: int) -> None:
    locale = api_client.get_locale(telegram_id)
    await state.set_state(ScheduleAddFSM.valid_until)
    keyboard = InlineKeyboardMarkup(inline_keyboard=[[
        InlineKeyboardButton(
            text=t("sch.valid_until_none_btn", locale),
            callback_data="sch_valid_until:none",
        ),
    ]])
    await message.answer(t("sch.valid_until_prompt", locale), reply_markup=keyboard)


@router.callback_query(ScheduleAddFSM.valid_until, F.data == "sch_valid_until:none")
async def fsm_valid_until_none(callback: CallbackQuery, state: FSMContext) -> None:
    await callback.answer()
    await state.update_data(sch_valid_until=None)
    await callback.message.delete()
    await _finish_schedule(callback.message, state, callback.from_user.id)


@router.message(ScheduleAddFSM.valid_until, F.text)
async def fsm_valid_until(message: Message, state: FSMContext) -> None:
    telegram_id = message.from_user.id
    locale = api_client.get_locale(telegram_id)
    try:
        parsed = date.fromisoformat(message.text.strip())
        await state.update_data(sch_valid_until=parsed.isoformat())
    except ValueError:
        await message.answer(t("sch.date_invalid", locale))
        return
    await _finish_schedule(message, state, telegram_id)


async def _finish_schedule(message: Message, state: FSMContext, telegram_id: int) -> None:
    locale = api_client.get_locale(telegram_id)
    data = await state.get_data()
    await state.clear()

    body = {
        "title": data["sch_name"],
        "weekdays": data["sch_days"],  # already sorted list
        "time_start": data["sch_time_start"],
        "time_end": data["sch_time_end"] or data["sch_time_start"],
        "valid_from": data.get("sch_valid_from"),
        "valid_until": data.get("sch_valid_until"),
    }

    result = await api_client.create_schedule(telegram_id, body)
    if not result:
        await message.answer(t("sch.create_failed", locale))
        return

    days_str = _days_label(result["weekdays"], locale)
    time_start = (result.get("time_start") or "")[:5]
    time_end = (result.get("time_end") or "")[:5]

    if time_end and time_end != time_start:
        await message.answer(
            t("sch.created", locale, title=result["title"], days=days_str,
              time_start=time_start, time_end=time_end),
            parse_mode="HTML",
        )
    else:
        await message.answer(
            t("sch.created_no_end", locale, title=result["title"], days=days_str,
              time_start=time_start),
            parse_mode="HTML",
        )


# ── Time validation helpers ───────────────────────────────────────────────────

def _valid_time(s: str) -> bool:
    parts = s.split(":")
    if len(parts) != 2:
        return False
    try:
        h, m = int(parts[0]), int(parts[1])
        return 0 <= h <= 23 and 0 <= m <= 59
    except ValueError:
        return False


def _normalise_time(s: str) -> str:
    """'8:00' → '08:00'"""
    h, m = s.split(":")
    return f"{int(h):02d}:{int(m):02d}"
