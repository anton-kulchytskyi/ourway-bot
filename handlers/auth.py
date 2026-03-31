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

from services import api_client

logger = logging.getLogger(__name__)
router = Router()


class RegisterStates(StatesGroup):
    waiting_for_name = State()


# ── /start ────────────────────────────────────────────────────────────────────

@router.message(CommandStart())
async def cmd_start(message: Message, state: FSMContext) -> None:
    args = message.text.split(maxsplit=1)[1] if " " in message.text else ""
    telegram_id = message.from_user.id
    first_name = message.from_user.first_name or "there"

    # ── Flow B: deep link with link token ────────────────────────────────────
    if args:
        link_token = args.strip()
        result = await api_client.link_telegram(link_token, telegram_id)
        if result is None:
            await message.answer(
                "❌ The link is invalid or has expired.\n"
                "Please generate a new one in the app: Settings → Connect Telegram."
            )
            return

        tokens = await api_client.bot_login(telegram_id)
        if tokens:
            api_client.save_token(telegram_id, tokens["access_token"])
            await message.answer(
                f"✅ Your Telegram account is now connected!\n\n"
                f"Welcome, {first_name}! Type /help to see what I can do."
            )
        else:
            await message.answer(
                "✅ Account connected! Send /start again to log in."
            )
        return

    # ── Flow C: returning user — try auto-login ───────────────────────────────
    tokens = await api_client.bot_login(telegram_id)
    if tokens:
        api_client.save_token(telegram_id, tokens["access_token"])
        await message.answer(
            f"👋 Welcome back, {first_name}!\n\n"
            "Type /help to see available commands."
        )
        return

    # ── Flow A: new user — start registration ────────────────────────────────
    await state.set_state(RegisterStates.waiting_for_name)
    await message.answer(
        f"👋 Hi, {first_name}! Welcome to OurWay — your family planner.\n\n"
        "Let's set up your account. What's your name?"
    )


@router.message(RegisterStates.waiting_for_name, F.text)
async def process_name(message: Message, state: FSMContext) -> None:
    name = message.text.strip()
    telegram_id = message.from_user.id

    if len(name) < 2:
        await message.answer("Please enter at least 2 characters.")
        return

    locale = message.from_user.language_code or "en"
    # Normalise: only use 'en' or 'uk', default to 'en'
    locale = "uk" if locale.startswith("uk") else "en"

    tokens = await api_client.telegram_register(telegram_id, name, locale)
    if tokens is None:
        # Already registered — just log in
        tokens = await api_client.bot_login(telegram_id)

    if tokens:
        api_client.save_token(telegram_id, tokens["access_token"])
        await state.clear()
        await message.answer(
            f"🎉 Welcome to OurWay, {name}!\n\n"
            "Your account is ready. Type /help to get started."
        )
    else:
        await state.clear()
        await message.answer(
            "Something went wrong. Please try /start again."
        )
