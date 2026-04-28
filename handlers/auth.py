"""
Handles Telegram account linking and registration flows.

Flow A — Telegram-first registration (new user, no account):
  /start → "What's your name?" → user replies → account created → logged in

Flow B — Deep link linking (user registered on web, links TG):
  /start <link_token> → account linked → auto-login

Flow C — Returning user:
  /start → auto-login via bot-login → welcome back

Flow D — Invite deep link (adult member invite):
  /start inv_TOKEN → fetch invite info → if returning user: accept immediately
                   → if new user: register (with name prompt) → accept → joined
"""
import logging

from aiogram import F, Router
from aiogram.filters import Command, CommandStart
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup, Message

from config import FRONTEND_URL
from keyboards import main_keyboard
from locales import t
from services import api_client

logger = logging.getLogger(__name__)
router = Router()


class RegisterStates(StatesGroup):
    waiting_for_name = State()


def _tg_locale(message: Message) -> str:
    """Detect locale from Telegram language code before the user is registered."""
    lc = message.from_user.language_code or "en"
    return "uk" if lc.startswith("uk") else "en"


def _web_login_keyboard(url: str, locale: str) -> InlineKeyboardMarkup:
    label = "Відкрити OurWay" if locale == "uk" else "Open OurWay"
    return InlineKeyboardMarkup(inline_keyboard=[[InlineKeyboardButton(text=label, url=url)]])


# ── /start ────────────────────────────────────────────────────────────────────

@router.message(CommandStart())
async def cmd_start(message: Message, state: FSMContext) -> None:
    args = message.text.split(maxsplit=1)[1] if " " in message.text else ""
    telegram_id = message.from_user.id
    first_name = message.from_user.first_name or "there"
    locale = _tg_locale(message)

    # ── Flow D: invite deep link (/start inv_TOKEN) ───────────────────────────
    if args and args.startswith("inv_"):
        inv_token = args[4:]  # strip "inv_" prefix
        inv_info = await api_client.get_invitation_info(inv_token)
        if not inv_info:
            await message.answer(t("invite.link_invalid", locale))
            return

        org_name = inv_info.get("org_name", "")
        space_name = inv_info.get("space_name") or ""
        inviter_name = inv_info.get("invited_by_name", "")
        # Display name: space if present, otherwise org
        display_name = space_name if space_name else org_name

        # Returning user — accept immediately
        tokens = await api_client.bot_login(telegram_id)
        if tokens:
            api_client.save_token(telegram_id, tokens["access_token"])
            me = await api_client.get_me(telegram_id)
            if me:
                api_client.save_locale(telegram_id, me.get("locale", locale))
                api_client.save_role(telegram_id, me.get("role", "member"))
                locale = api_client.get_locale(telegram_id)
            accepted = await api_client.accept_invitation(telegram_id, inv_token)
            if accepted:
                await message.answer(t("invite.joined", locale, space=display_name))
            else:
                await message.answer(t("invite.accept_failed", locale))
            await message.answer(t("auth.keyboard_hint", locale), reply_markup=main_keyboard())
            return

        # New user — start registration, carry the invite token
        await state.update_data(inv_token=inv_token, inv_space=display_name)
        await state.set_state(RegisterStates.waiting_for_name)
        await message.answer(
            t("invite.register_prompt", locale, space=display_name, inviter=inviter_name)
        )
        return

    # ── Flow B: deep link with link token ────────────────────────────────────
    if args:
        link_token = args.strip()
        result = await api_client.link_telegram(link_token, telegram_id)
        if result is None:
            await message.answer(t("auth.link_invalid", locale))
            return

        tokens = await api_client.bot_login(telegram_id)
        if tokens:
            api_client.save_token(telegram_id, tokens["access_token"])
            me = await api_client.get_me(telegram_id)
            if me:
                api_client.save_locale(telegram_id, me.get("locale", locale))
                api_client.save_role(telegram_id, me.get("role", "member"))
                locale = api_client.get_locale(telegram_id)
            await message.answer(t("auth.connected_welcome", locale, name=first_name))
            await message.answer(t("auth.keyboard_hint", locale), reply_markup=main_keyboard())
        else:
            await message.answer(t("auth.connected_start_again", locale))
        return

    # ── Flow C: returning user — try auto-login ───────────────────────────────
    tokens = await api_client.bot_login(telegram_id)
    if tokens:
        api_client.save_token(telegram_id, tokens["access_token"])
        me = await api_client.get_me(telegram_id)
        if me:
            api_client.save_locale(telegram_id, me.get("locale", locale))
            api_client.save_role(telegram_id, me.get("role", "member"))
            locale = api_client.get_locale(telegram_id)
        web_token = await api_client.get_web_token(telegram_id)
        if web_token:
            url = f"{FRONTEND_URL.rstrip('/')}/api/auth/callback?token={web_token}"
            await message.answer(
                t("auth.welcome_back", locale, name=first_name),
                reply_markup=_web_login_keyboard(url, locale),
            )
        else:
            await message.answer(t("auth.welcome_back", locale, name=first_name))
        await message.answer(t("auth.keyboard_hint", locale), reply_markup=main_keyboard())
        return

    # ── Flow A: new user — start registration ────────────────────────────────
    await state.set_state(RegisterStates.waiting_for_name)
    await message.answer(t("auth.hello_new_user", locale, name=first_name))


@router.message(Command("web"))
async def cmd_web(message: Message) -> None:
    """Generate a fresh web login link for the current user."""
    telegram_id = message.from_user.id
    locale = api_client.get_locale(telegram_id)

    if not await api_client.ensure_token(telegram_id):
        await message.answer(t("common.not_logged_in", locale))
        return

    web_token = await api_client.get_web_token(telegram_id)
    if not web_token:
        await message.answer(t("auth.error", locale))
        return

    url = f"{FRONTEND_URL.rstrip('/')}/api/auth/callback?token={web_token}"
    label = "Відкрити OurWay" if locale == "uk" else "Open OurWay"
    await message.answer(
        label,
        reply_markup=InlineKeyboardMarkup(
            inline_keyboard=[[InlineKeyboardButton(text=f"🌐 {label}", url=url)]]
        ),
    )


@router.message(RegisterStates.waiting_for_name, F.text)
async def process_name(message: Message, state: FSMContext) -> None:
    name = message.text.strip()
    telegram_id = message.from_user.id
    locale = _tg_locale(message)

    if len(name) < 2:
        await message.answer(t("common.min_2_chars", locale))
        return

    # Normalise: only use 'en' or 'uk', default to 'en'
    reg_locale = "uk" if locale == "uk" else "en"

    tokens = await api_client.telegram_register(telegram_id, name, reg_locale)
    if tokens is None:
        # Already registered — just log in
        tokens = await api_client.bot_login(telegram_id)

    if tokens:
        api_client.save_token(telegram_id, tokens["access_token"])
        api_client.save_locale(telegram_id, reg_locale)
        fsm_data = await state.get_data()
        inv_token = fsm_data.get("inv_token")
        inv_space = fsm_data.get("inv_space", "")
        await state.clear()

        if inv_token:
            accepted = await api_client.accept_invitation(telegram_id, inv_token)
            if accepted:
                await message.answer(t("invite.registered_joined", reg_locale, name=name, space=inv_space))
            else:
                await message.answer(t("auth.registered", reg_locale, name=name))
            await message.answer(t("auth.keyboard_hint", reg_locale), reply_markup=main_keyboard())
            return

        web_token = await api_client.get_web_token(telegram_id)
        if web_token:
            url = f"{FRONTEND_URL.rstrip('/')}/api/auth/callback?token={web_token}"
            await message.answer(
                t("auth.registered", reg_locale, name=name),
                reply_markup=_web_login_keyboard(url, reg_locale),
            )
        else:
            await message.answer(t("auth.registered", reg_locale, name=name))
        await message.answer(t("auth.keyboard_hint", reg_locale), reply_markup=main_keyboard())
    else:
        await state.clear()
        await message.answer(t("auth.error", locale))
