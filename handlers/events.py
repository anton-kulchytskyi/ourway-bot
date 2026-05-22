"""
/events — list upcoming events
/add_event — FSM: title → date → time → participants → create
"""
import logging
from datetime import date, timedelta

from aiogram import F, Router
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from aiogram.types import CallbackQuery, InlineKeyboardButton, InlineKeyboardMarkup, Message

from handlers.scheduling_helpers import parse_event_date, time_hour_keyboard, time_minute_keyboard
from locales import t
from services import api_client

logger = logging.getLogger(__name__)
router = Router()


class EventAddFSM(StatesGroup):
    title = State()
    date = State()
    time = State()
    participants = State()
    reminder = State()


# ── Helpers ───────────────────────────────────────────────────────────────────

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
    h, m = s.split(":")
    return f"{int(h):02d}:{int(m):02d}"


def _fmt_event(event: dict) -> str:
    title = event.get("title", "")
    date_str = event.get("date") or ""
    time_str = (event.get("time_start") or "")[:5]
    parts = []
    if date_str:
        parts.append(date_str)
    if time_str:
        parts.append(time_str)
    prefix = " ".join(parts)
    return f"📅 {prefix + ' ' if prefix else ''}{title}"


def _participants_keyboard(
    members: list[dict],
    selected: set[int],
    my_id: int,
    locale: str,
) -> InlineKeyboardMarkup:
    """Toggle keyboard for participants. Selected show ✅ prefix."""
    rows = []
    for m in members:
        uid = m["id"]
        name = t("event.participants_me_btn", locale) if uid == my_id else m["name"]
        prefix = "✅ " if uid in selected else ""
        rows.append([InlineKeyboardButton(
            text=f"{prefix}{name}",
            callback_data=f"ev_part:{uid}",
        )])
    rows.append([InlineKeyboardButton(
        text=t("event.participants_done_btn", locale),
        callback_data="ev_part:done",
    )])
    rows.append([InlineKeyboardButton(
        text=t("event.cancel_btn", locale),
        callback_data="ev_cancel",
    )])
    return InlineKeyboardMarkup(inline_keyboard=rows)


# ── /events ───────────────────────────────────────────────────────────────────

@router.message(Command("events"))
async def cmd_events(message: Message) -> None:
    telegram_id = message.from_user.id
    if not await api_client.ensure_token(telegram_id):
        await message.answer(t("common.not_logged_in", api_client.get_locale(telegram_id)))
        return

    locale = api_client.get_locale(telegram_id)
    events = await api_client.get_events(telegram_id)
    if events is None:
        await message.answer(t("event.load_failed", locale))
        return

    today = date.today().isoformat()
    upcoming = [e for e in events if not e.get("date") or e["date"] >= today]
    upcoming.sort(key=lambda e: (e.get("date") is None, e.get("date") or ""))

    if not upcoming:
        await message.answer(t("event.no_events", locale))
        return

    me = await api_client.get_me(telegram_id)
    is_child = me and me.get("role") == "child"

    lines = [t("event.list_header", locale), ""]
    for e in upcoming:
        lines.append(_fmt_event(e))

    if not is_child:
        keyboard = InlineKeyboardMarkup(inline_keyboard=[[
            InlineKeyboardButton(
                text=t("event.delete_btn", locale),
                callback_data="ev_action:delete",
            ),
        ]])
        await message.answer("\n".join(lines), parse_mode="HTML", reply_markup=keyboard)
    else:
        await message.answer("\n".join(lines), parse_mode="HTML")


# ── Delete flow ───────────────────────────────────────────────────────────────

@router.callback_query(F.data == "ev_action:delete")
async def cb_delete_list(callback: CallbackQuery) -> None:
    await callback.answer()
    telegram_id = callback.from_user.id
    locale = api_client.get_locale(telegram_id)

    events = await api_client.get_events(telegram_id)
    if not events:
        await callback.message.answer(t("event.no_events", locale))
        return

    today = date.today().isoformat()
    upcoming = [e for e in events if not e.get("date") or e["date"] >= today]
    upcoming.sort(key=lambda e: (e.get("date") is None, e.get("date") or ""))

    buttons = []
    for e in upcoming:
        label = e["title"]
        if e.get("date"):
            label += f" ({e['date']})"
        buttons.append([InlineKeyboardButton(
            text=label,
            callback_data=f"ev_del:{e['id']}:{e['title']}",
        )])

    await callback.message.answer(
        t("event.pick_to_delete", locale),
        reply_markup=InlineKeyboardMarkup(inline_keyboard=buttons),
    )


@router.callback_query(F.data.startswith("ev_del:"))
async def cb_do_delete(callback: CallbackQuery) -> None:
    _, event_id, title = callback.data.split(":", 2)
    telegram_id = callback.from_user.id
    locale = api_client.get_locale(telegram_id)
    await callback.message.delete()

    ok = await api_client.delete_event(telegram_id, int(event_id))
    if ok:
        await callback.message.answer(
            t("event.deleted", locale, title=title), parse_mode="HTML"
        )
    else:
        await callback.message.answer(t("event.delete_failed", locale))
    await callback.answer()


# ── /add_event FSM ────────────────────────────────────────────────────────────

@router.message(Command("add_event"))
async def cmd_add_event(message: Message, state: FSMContext) -> None:
    telegram_id = message.from_user.id
    if not await api_client.ensure_token(telegram_id):
        await message.answer(t("common.not_logged_in", api_client.get_locale(telegram_id)))
        return

    locale = api_client.get_locale(telegram_id)

    me = await api_client.get_me(telegram_id)
    if me and me.get("role") == "child":
        await message.answer(t("event.load_failed", locale))
        return

    await state.set_state(EventAddFSM.title)
    await message.answer(t("event.title_prompt", locale))


@router.message(EventAddFSM.title, F.text)
async def fsm_title(message: Message, state: FSMContext) -> None:
    title = message.text.strip()
    telegram_id = message.from_user.id
    locale = api_client.get_locale(telegram_id)

    if len(title) < 2:
        await message.answer(t("common.min_2_chars", locale))
        return

    await state.update_data(ev_title=title)
    await state.set_state(EventAddFSM.date)

    today = date.today().isoformat()
    tomorrow = (date.today() + timedelta(days=1)).isoformat()

    keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [
            InlineKeyboardButton(
                text=t("event.date_today_btn", locale),
                callback_data=f"ev_date:{today}",
            ),
            InlineKeyboardButton(
                text=t("event.date_tomorrow_btn", locale),
                callback_data=f"ev_date:{tomorrow}",
            ),
        ],
        [
            InlineKeyboardButton(
                text=t("event.date_other_btn", locale),
                callback_data="ev_date:other",
            ),
        ],
        [
            InlineKeyboardButton(
                text=t("event.cancel_btn", locale),
                callback_data="ev_cancel",
            ),
        ],
    ])
    await message.answer(
        t("event.date_prompt", locale, title=title),
        parse_mode="HTML",
        reply_markup=keyboard,
    )


@router.callback_query(EventAddFSM.date, F.data.startswith("ev_date:"))
async def fsm_date_btn(callback: CallbackQuery, state: FSMContext) -> None:
    await callback.answer()
    value = callback.data.split(":", 1)[1]
    locale = api_client.get_locale(callback.from_user.id)

    if value == "other":
        await callback.message.delete()
        await callback.message.answer(t("event.date_other_hint", locale))
        # stay in EventAddFSM.date — text handler below will catch the typed date
        return

    # legacy "skip" — kept for in-flight sessions
    await state.update_data(ev_date=None if value == "skip" else value)
    await callback.message.delete()
    await _ask_time(callback.message, state, callback.from_user.id, locale)


@router.message(EventAddFSM.date, F.text)
async def fsm_date_text(message: Message, state: FSMContext) -> None:
    telegram_id = message.from_user.id
    locale = api_client.get_locale(telegram_id)
    parsed = parse_event_date(message.text)
    if parsed is None:
        await message.answer(t("event.date_invalid", locale))
        return
    await state.update_data(ev_date=parsed.isoformat())
    await _ask_time(message, state, telegram_id, locale)


# ── Time picker ───────────────────────────────────────────────────────────────

async def _ask_time(message: Message, state: FSMContext, telegram_id: int, locale: str) -> None:
    await state.set_state(EventAddFSM.time)
    await message.answer(
        t("event.time_prompt", locale),
        reply_markup=time_hour_keyboard(locale, "ev_th", skip_data="ev_time:skip"),
    )


@router.callback_query(EventAddFSM.time, F.data.startswith("ev_th:"))
async def fsm_time_hour(callback: CallbackQuery, state: FSMContext) -> None:
    value = callback.data.split(":", 1)[1]
    locale = api_client.get_locale(callback.from_user.id)

    if value == "back":
        await callback.message.edit_text(
            t("event.time_prompt", locale),
            reply_markup=time_hour_keyboard(locale, "ev_th", skip_data="ev_time:skip"),
        )
        await callback.answer()
        return

    hour = int(value)
    await callback.message.edit_text(
        t("time.minute_prompt", locale, hour=f"{hour:02d}"),
        reply_markup=time_minute_keyboard(hour, locale, "ev_tm", "ev_th", skip_data="ev_time:skip"),
    )
    await callback.answer()


@router.callback_query(EventAddFSM.time, F.data.startswith("ev_tm:"))
async def fsm_time_minute(callback: CallbackQuery, state: FSMContext) -> None:
    _, h, m = callback.data.split(":")
    time_str = f"{int(h):02d}:{int(m):02d}"
    await state.update_data(ev_time=time_str)
    await callback.message.delete()
    await _ask_participants(callback.message, state, callback.from_user.id)
    await callback.answer()


@router.callback_query(EventAddFSM.time, F.data == "ev_time:skip")
async def fsm_time_skip(callback: CallbackQuery, state: FSMContext) -> None:
    await callback.answer()
    await state.update_data(ev_time=None)
    await callback.message.delete()
    await _ask_participants(callback.message, state, callback.from_user.id)


@router.message(EventAddFSM.time, F.text)
async def fsm_time_text(message: Message, state: FSMContext) -> None:
    telegram_id = message.from_user.id
    locale = api_client.get_locale(telegram_id)
    time_str = message.text.strip()

    if not _valid_time(time_str):
        await message.answer(t("event.time_invalid", locale))
        return

    await state.update_data(ev_time=_normalise_time(time_str))
    await _ask_participants(message, state, telegram_id)


# ── Reminder ─────────────────────────────────────────────────────────────────

def _reminder_keyboard(locale: str) -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(inline_keyboard=[
        [
            InlineKeyboardButton(text=t("event.remind_15_btn", locale), callback_data="ev_remind:15"),
            InlineKeyboardButton(text=t("event.remind_30_btn", locale), callback_data="ev_remind:30"),
            InlineKeyboardButton(text=t("event.remind_60_btn", locale), callback_data="ev_remind:60"),
        ],
        [
            InlineKeyboardButton(text=t("event.remind_skip_btn", locale), callback_data="ev_remind:skip"),
        ],
    ])


# ── Participants ──────────────────────────────────────────────────────────────

async def _ask_participants(message: Message, state: FSMContext, telegram_id: int) -> None:
    locale = api_client.get_locale(telegram_id)

    me = await api_client.get_me(telegram_id)
    my_id = me["id"] if me else 0

    members_raw = await api_client.get_family_members(telegram_id) or []
    members = [{"id": my_id, "name": "me"}] + [
        m for m in members_raw if m["id"] != my_id
    ]
    selected = {my_id}

    await state.update_data(ev_members=members, ev_my_id=my_id, ev_participants=list(selected))
    await state.set_state(EventAddFSM.participants)

    await message.answer(
        t("event.participants_prompt", locale),
        reply_markup=_participants_keyboard(members, selected, my_id, locale),
    )


@router.callback_query(EventAddFSM.participants, F.data.startswith("ev_part:"))
async def fsm_toggle_participant(callback: CallbackQuery, state: FSMContext) -> None:
    value = callback.data.split(":", 1)[1]
    telegram_id = callback.from_user.id
    locale = api_client.get_locale(telegram_id)
    data = await state.get_data()

    if value == "done":
        await callback.answer()
        await callback.message.delete()
        await _ask_reminder(callback.message, state, telegram_id)
        return

    uid = int(value)
    selected: set[int] = set(data.get("ev_participants", []))
    if uid in selected:
        selected.discard(uid)
    else:
        selected.add(uid)

    await state.update_data(ev_participants=list(selected))
    members = data.get("ev_members", [])
    my_id = data.get("ev_my_id", 0)

    await callback.message.edit_reply_markup(
        reply_markup=_participants_keyboard(members, selected, my_id, locale)
    )
    await callback.answer()


async def _ask_reminder(message: Message, state: FSMContext, telegram_id: int) -> None:
    locale = api_client.get_locale(telegram_id)
    await state.set_state(EventAddFSM.reminder)
    await message.answer(
        t("event.remind_prompt", locale),
        reply_markup=_reminder_keyboard(locale),
    )


@router.callback_query(EventAddFSM.reminder, F.data.startswith("ev_remind:"))
async def fsm_reminder(callback: CallbackQuery, state: FSMContext) -> None:
    await callback.answer()
    value = callback.data.split(":", 1)[1]
    telegram_id = callback.from_user.id

    remind_before_min = None if value == "skip" else int(value)
    await state.update_data(ev_remind_before_min=remind_before_min)
    await callback.message.delete()
    await _finish_event(callback.message, state, telegram_id)


async def _finish_event(message: Message, state: FSMContext, telegram_id: int) -> None:
    locale = api_client.get_locale(telegram_id)
    data = await state.get_data()
    await state.clear()

    body = {
        "title": data["ev_title"],
        "date": data.get("ev_date"),
        "time_start": data.get("ev_time"),
        "participants": data.get("ev_participants", []),
        "remind_before_min": data.get("ev_remind_before_min"),
    }

    result = await api_client.create_event(telegram_id, body)
    if not result:
        await message.answer(t("event.create_failed", locale))
        return

    date_str = result.get("date") or ""
    time_str = (result.get("time_start") or "")[:5]
    date_part = f"\n📅 {date_str}" if date_str else ""
    time_part = f" {time_str}" if time_str and date_str else (f"\n🕐 {time_str}" if time_str else "")

    await message.answer(
        t("event.created", locale, title=result["title"], date=date_part, time=time_part),
        parse_mode="HTML",
    )


# ── Cancel ────────────────────────────────────────────────────────────────────

@router.callback_query(F.data == "ev_cancel")
async def cb_cancel(callback: CallbackQuery, state: FSMContext) -> None:
    await state.clear()
    await callback.message.delete()
    await callback.answer()
    locale = api_client.get_locale(callback.from_user.id)
    await callback.message.answer(t("common.cancelled", locale))
