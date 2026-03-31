"""
Handles Telegram account linking flow.

Flow:
  1. User clicks deep link: t.me/bot?start=<link_token>
  2. Bot receives /start <link_token>
  3. Bot calls POST /users/telegram/link  → TG account linked
  4. Bot calls POST /auth/bot-login       → gets JWT, stores in memory
  5. User can now use all bot commands
"""
import logging

from aiogram import Router
from aiogram.filters import CommandStart
from aiogram.types import Message

from services import api_client

logger = logging.getLogger(__name__)
router = Router()


@router.message(CommandStart())
async def cmd_start(message: Message) -> None:
    args = message.text.split(maxsplit=1)[1] if " " in message.text else ""
    telegram_id = message.from_user.id
    first_name = message.from_user.first_name or "there"

    # ── Case 1: deep link with link token ────────────────────────────────────
    if args:
        link_token = args.strip()
        result = await api_client.link_telegram(link_token, telegram_id)
        if result is None:
            await message.answer(
                "❌ The link is invalid or has expired.\n"
                "Please generate a new one in the app (Settings → Connect Telegram)."
            )
            return

        # Auto-login after linking
        tokens = await api_client.bot_login(telegram_id)
        if tokens:
            api_client.save_token(telegram_id, tokens["access_token"])
            await message.answer(
                f"✅ Your Telegram account is now linked!\n\n"
                f"Welcome, {first_name}! Type /help to see what I can do."
            )
        else:
            await message.answer(
                "✅ Account linked! But I couldn't log you in automatically.\n"
                "Please try /login or restart the bot."
            )
        return

    # ── Case 2: plain /start — try auto-login if already linked ──────────────
    tokens = await api_client.bot_login(telegram_id)
    if tokens:
        api_client.save_token(telegram_id, tokens["access_token"])
        await message.answer(
            f"👋 Welcome back, {first_name}!\n\n"
            "Type /help to see available commands."
        )
    else:
        await message.answer(
            f"👋 Hi, {first_name}! I'm the OurWay bot.\n\n"
            "To get started, connect your account:\n"
            "1. Open the OurWay app\n"
            "2. Go to Settings → Connect Telegram\n"
            "3. Click the link — it will open this chat automatically."
        )
