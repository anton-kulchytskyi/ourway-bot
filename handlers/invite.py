"""
/invite — invite an adult member to a space.

Flow:
  /invite → list of owned spaces → pick role (editor / viewer)
  → create invitation via API → send TG deep link + web link
"""
import logging

from aiogram import F, Router
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from aiogram.types import (
    CallbackQuery,
    InlineKeyboardButton,
    InlineKeyboardMarkup,
    Message,
)

from config import FRONTEND_URL, BOT_USERNAME
from locales import t
from services import api_client

logger = logging.getLogger(__name__)
router = Router()


class InviteFSM(StatesGroup):
    pick_space = State()
    pick_role = State()


@router.message(Command("invite"))
async def cmd_invite(message: Message, state: FSMContext) -> None:
    telegram_id = message.from_user.id
    if not await api_client.ensure_token(telegram_id):
        await message.answer(t("common.not_logged_in", api_client.get_locale(telegram_id)))
        return

    locale = api_client.get_locale(telegram_id)
    spaces = await api_client.get_spaces(telegram_id)
    if spaces is None:
        await message.answer(t("space.load_failed", locale))
        return

    owned = [s for s in spaces if s.get("my_role") == "owner"]
    if not owned:
        await message.answer(t("invite.no_owned_spaces", locale))
        return

    buttons = [
        [InlineKeyboardButton(
            text=f"{s.get('emoji') or ''} {s['name']}".strip(),
            callback_data=f"invs:{s['id']}",
        )]
        for s in owned
    ]
    buttons.append([InlineKeyboardButton(text=t("invite.cancel_btn", locale), callback_data="invs:cancel")])

    await state.set_state(InviteFSM.pick_space)
    await message.answer(
        t("invite.pick_space", locale),
        reply_markup=InlineKeyboardMarkup(inline_keyboard=buttons),
    )


@router.callback_query(InviteFSM.pick_space, F.data.startswith("invs:"))
async def got_space(callback: CallbackQuery, state: FSMContext) -> None:
    value = callback.data.split(":")[1]
    locale = api_client.get_locale(callback.from_user.id)
    await callback.message.delete()

    if value == "cancel":
        await state.clear()
        await callback.message.answer(t("common.cancelled", locale))
        return

    await state.update_data(space_id=int(value))
    await state.set_state(InviteFSM.pick_role)

    kb = InlineKeyboardMarkup(inline_keyboard=[
        [
            InlineKeyboardButton(text=t("invite.role_editor", locale), callback_data="invr:editor"),
            InlineKeyboardButton(text=t("invite.role_viewer", locale), callback_data="invr:viewer"),
        ],
        [InlineKeyboardButton(text=t("invite.cancel_btn", locale), callback_data="invr:cancel")],
    ])
    await callback.message.answer(t("invite.pick_role", locale), reply_markup=kb)


@router.callback_query(InviteFSM.pick_role, F.data.startswith("invr:"))
async def got_role(callback: CallbackQuery, state: FSMContext) -> None:
    value = callback.data.split(":")[1]
    locale = api_client.get_locale(callback.from_user.id)
    await callback.message.delete()

    if value == "cancel":
        await state.clear()
        await callback.message.answer(t("common.cancelled", locale))
        return

    data = await state.get_data()
    space_id = data["space_id"]
    await state.clear()

    result = await api_client.create_invitation(callback.from_user.id, space_id, value)
    if result is None:
        await callback.message.answer(t("invite.create_failed", locale))
        return

    token = result["token"]
    tg_link = f"https://t.me/{BOT_USERNAME}?start=inv_{token}"
    web_link = f"{FRONTEND_URL.rstrip('/')}/{locale}/invite/{token}"
    role_label = t(f"invite.role_{value}", locale)

    kb = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text=t("invite.open_tg_btn", locale), url=tg_link)],
        [InlineKeyboardButton(text=t("invite.open_web_btn", locale), url=web_link)],
    ])

    await callback.message.answer(
        t("invite.created", locale, role=role_label),
        parse_mode="HTML",
        reply_markup=kb,
    )
