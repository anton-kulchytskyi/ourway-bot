"""
Space management: /spaces, create space FSM
"""
import logging

from aiogram import F, Router
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from aiogram.types import CallbackQuery, InlineKeyboardButton, InlineKeyboardMarkup, Message

from locales import t
from services import api_client

logger = logging.getLogger(__name__)
router = Router()


class CreateSpaceStates(StatesGroup):
    waiting_for_name = State()
    waiting_for_emoji = State()


# ── /spaces ───────────────────────────────────────────────────────────────────

@router.message(Command("spaces"))
async def cmd_spaces(message: Message) -> None:
    telegram_id = message.from_user.id
    if not await api_client.ensure_token(telegram_id):
        await message.answer(t("common.not_logged_in", api_client.get_locale(telegram_id)))
        return

    locale = api_client.get_locale(telegram_id)
    spaces = await api_client.get_spaces(telegram_id)
    if spaces is None:
        await message.answer(t("space.load_failed", locale))
        return

    create_row = [InlineKeyboardButton(text=t("space.create_new_btn", locale), callback_data="create_space")]

    if not spaces:
        await message.answer(t("space.no_spaces", locale), reply_markup=InlineKeyboardMarkup(inline_keyboard=[create_row]))
        return

    rows = []
    for s in spaces:
        emoji = s.get("emoji") or "📁"
        rows.append([InlineKeyboardButton(
            text=f"{emoji} {s['name']}  {t('space.tasks_btn', locale)}",
            callback_data=f"space_tasks:{s['id']}",
        )])
    rows.append(create_row)

    lines = [t("space.list_header", locale), ""]
    for s in spaces:
        emoji = s.get("emoji") or "📁"
        lines.append(f"{emoji} {s['name']}")

    await message.answer(
        "\n".join(lines),
        parse_mode="HTML",
        reply_markup=InlineKeyboardMarkup(inline_keyboard=rows),
    )


@router.callback_query(F.data.startswith("space_tasks:"))
async def cb_space_tasks(callback: CallbackQuery) -> None:
    await callback.answer()
    telegram_id = callback.from_user.id
    locale = api_client.get_locale(telegram_id)

    space_id = int(callback.data.split(":")[1])

    spaces = await api_client.get_spaces(telegram_id)
    space = next((s for s in spaces if s["id"] == space_id), None) if spaces else None

    tasks = await api_client.get_space_tasks(telegram_id, space_id)
    if tasks is None:
        await callback.message.answer(t("space.tasks_load_failed", locale))
        return

    active = [tk for tk in tasks if tk["status"] != "done"]
    if not active:
        await callback.message.answer(t("space.tasks_empty", locale))
        return

    # Build assignee name map: fetch family members + self
    members = await api_client.get_family_members(telegram_id) or []
    me = await api_client.get_me(telegram_id)
    name_map: dict[int, str] = {m["id"]: m["name"] for m in members}
    if me:
        name_map[me["id"]] = me["name"]

    STATUS_ORDER = ["in_progress", "todo", "blocked", "backlog"]
    STATUS_LABEL = {
        "in_progress": t("space.status_in_progress", locale),
        "todo": t("space.status_todo", locale),
        "blocked": t("space.status_blocked", locale),
        "backlog": t("space.status_backlog", locale),
    }

    emoji = (space.get("emoji") or "📁") if space else "📁"
    name = space["name"] if space else f"#{space_id}"
    lines = [t("space.tasks_header", locale, emoji=emoji, name=name), ""]

    for status in STATUS_ORDER:
        group = [tk for tk in active if tk["status"] == status]
        if not group:
            continue
        lines.append(STATUS_LABEL[status])
        for tk in group:
            assignee_id = tk.get("assignee_id")
            assignee = f" — 👤 {name_map[assignee_id]}" if assignee_id and assignee_id in name_map else ""
            lines.append(f"  • {tk['title']}{assignee}")
        lines.append("")

    await callback.message.answer("\n".join(lines).strip(), parse_mode="HTML")


# ── Create space flow ─────────────────────────────────────────────────────────

@router.callback_query(F.data == "create_space")
async def cb_create_space(callback: CallbackQuery, state: FSMContext) -> None:
    await callback.answer()
    locale = api_client.get_locale(callback.from_user.id)
    await state.set_state(CreateSpaceStates.waiting_for_name)
    await callback.message.answer(t("space.name_prompt", locale))


@router.message(CreateSpaceStates.waiting_for_name, F.text)
async def process_space_name(message: Message, state: FSMContext) -> None:
    name = message.text.strip()
    telegram_id = message.from_user.id
    locale = api_client.get_locale(telegram_id)

    if len(name) < 2:
        await message.answer(t("common.min_2_chars", locale))
        return

    await state.update_data(space_name=name)
    await state.set_state(CreateSpaceStates.waiting_for_emoji)

    keyboard = InlineKeyboardMarkup(inline_keyboard=[[
        InlineKeyboardButton(
            text=t("space.skip_btn", locale),
            callback_data="space_emoji_skip",
        ),
    ]])
    await message.answer(
        t("space.emoji_prompt", locale, name=name),
        parse_mode="HTML",
        reply_markup=keyboard,
    )


@router.callback_query(F.data == "space_emoji_skip")
async def cb_skip_emoji(callback: CallbackQuery, state: FSMContext) -> None:
    await callback.answer()
    data = await state.get_data()
    await _finish_create_space(callback.message, state, callback.from_user.id, data["space_name"], None)


@router.message(CreateSpaceStates.waiting_for_emoji, F.text)
async def process_space_emoji(message: Message, state: FSMContext) -> None:
    emoji = message.text.strip()
    data = await state.get_data()
    await _finish_create_space(message, state, message.from_user.id, data["space_name"], emoji)


async def _finish_create_space(
    message: Message, state: FSMContext,
    telegram_id: int, name: str, emoji: str | None,
) -> None:
    locale = api_client.get_locale(telegram_id)
    space = await api_client.create_space(telegram_id, name, emoji)
    await state.clear()
    if space:
        icon = space.get("emoji") or "📁"
        await message.answer(
            t("space.created", locale, emoji=icon, name=space["name"]),
            parse_mode="HTML",
        )
    else:
        await message.answer(t("space.create_failed", locale))
