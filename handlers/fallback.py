"""
Catch-all handlers for unhandled messages, callbacks, and errors.
These run last (router included after all others) and improve log visibility.
"""
import logging

from aiogram import Router
from aiogram.types import CallbackQuery, ErrorEvent, Message

from locales import t
from services import api_client

logger = logging.getLogger(__name__)
router = Router()


@router.message()
async def unhandled_message(message: Message) -> None:
    user_id = message.from_user.id if message.from_user else "?"
    content_type = message.content_type
    preview = repr(message.text[:80]) if message.text else f"[{content_type}]"
    logger.info("Unhandled message user=%s type=%s content=%s", user_id, content_type, preview)

    if message.text and message.from_user:
        locale = api_client.get_locale(message.from_user.id)
        await message.answer(t("common.unknown_command", locale), parse_mode="HTML")


@router.callback_query()
async def unhandled_callback(callback: CallbackQuery) -> None:
    logger.warning(
        "Unhandled callback user=%s data=%r msg_id=%s",
        callback.from_user.id,
        callback.data,
        callback.message.message_id if callback.message else "?",
    )
    await callback.answer()


async def error_handler(event: ErrorEvent) -> None:
    update_id = event.update.update_id if event.update else "?"
    logger.exception("Unhandled exception in update %s: %s", update_id, event.exception)
