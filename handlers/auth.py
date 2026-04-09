"""
Handles Telegram account linking and registration flows.

Flow A — Telegram-first registration (new user, no account):
  /start → "What's your name?" → user replies → account created → logged in

Flow B — Deep link linking (user registered on web, links TG):
  /start <link_token> → account linked → auto-login

Flow C — Returning user:
  /start → auto-login via bot-login → welcome back
"""
import logging

from aiogram import F, Router
from aiogram.filters import CommandStart
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from aiogram.types import Message

from config import FRONTEND_URL
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


# ── /start ────────────────────────────────────────────────────────────────────

@router.message(CommandStart())
async def cmd_start(message: Message, state: FSMContext) -> None:
    args = message.text.split(maxsplit=1)[1] if " " in message.text else ""
    telegram_id = message.from_user.id
    first_name = message.from_user.first_name or "there"
    locale = _tg_locale(message)

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
                locale = api_client.get_locale(telegram_id)
            await message.answer(t("auth.connected_welcome", locale, name=first_name))
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
            locale = api_client.get_locale(telegram_id)
        await message.answer(t("auth.welcome_back", locale, name=first_name))
        return

    # ── Flow A: new user — start registration ────────────────────────────────
    await state.set_state(RegisterStates.waiting_for_name)
    await message.answer(t("auth.hello_new_user", locale, name=first_name))


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
        await state.clear()
        await message.answer(t("auth.registered", reg_locale, name=name))
        web_token = await api_client.get_web_token(telegram_id)
        if web_token:
            url = f"{FRONTEND_URL.rstrip('/')}/api/auth/callback?token={web_token}"
            await message.answer(t("auth.web_login_link", reg_locale, url=url))
    else:
        await state.clear()
        await message.answer(t("auth.error", locale))
