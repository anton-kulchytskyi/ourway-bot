"""
/kids — show all children in the family with their active tasks.

Shows: managed children + children with autonomy_level 1 or 2.
Autonomous children (level 3) manage themselves — not shown here.
Visible to all family members (owner + member).
"""
import logging

from aiogram import Router
from aiogram.filters import Command
from aiogram.types import Message

from locales import t
from services import api_client

logger = logging.getLogger(__name__)
router = Router()

STATUS_EMOJI = {
    "backlog": "📋",
    "todo": "📝",
    "in_progress": "🔄",
    "blocked": "🚫",
    "done": "✅",
}


def _is_visible_child(user: dict) -> bool:
    """Children we actively manage: managed profiles + autonomy level 1 or 2."""
    if user.get("role") != "child":
        return False
    if user.get("is_managed"):
        return True
    autonomy = user.get("autonomy_level")
    return autonomy in (1, 2)


@router.message(Command("kids"))
async def cmd_kids(message: Message) -> None:
    telegram_id = message.from_user.id
    if not await api_client.ensure_token(telegram_id):
        await message.answer(t("common.not_logged_in", api_client.get_locale(telegram_id)))
        return

    locale = api_client.get_locale(telegram_id)
    members = await api_client.get_family_members(telegram_id)
    if members is None:
        await message.answer(t("kids.load_failed", locale))
        return

    children = [m for m in members if _is_visible_child(m)]
    if not children:
        await message.answer(t("kids.no_children", locale))
        return

    lines = [t("kids.header", locale)]

    for child in children:
        name = child["name"]
        managed = child.get("is_managed", False)
        tag = t("kids.managed_tag", locale) if managed else ""
        lines += ["", f"👤 <b>{name}</b>{tag}"]

        tasks = await api_client.get_child_tasks(telegram_id, child["id"])
        if tasks is None:
            lines.append(t("kids.tasks_load_failed", locale))
            continue

        active = [task for task in tasks if task.get("status") != "done"]
        if not active:
            lines.append(t("kids.no_active_tasks", locale))
        else:
            for task in active:
                emoji = STATUS_EMOJI.get(task.get("status", ""), "•")
                lines.append(f"  {emoji} #{task['id']} {task['title']}")

    lines += ["", t("kids.footer", locale)]
    await message.answer("\n".join(lines), parse_mode="HTML")
