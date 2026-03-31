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
    if api_client.get_token(telegram_id) is None:
        await message.answer("Please send /start first to log in.")
        return

    members = await api_client.get_family_members(telegram_id)
    if members is None:
        await message.answer("❌ Could not load family members.")
        return

    children = [m for m in members if _is_visible_child(m)]
    if not children:
        await message.answer(
            "No children in your family yet.\n\n"
            "Use /add_child to add one."
        )
        return

    lines = ["<b>Kids' tasks:</b>"]

    for child in children:
        name = child["name"]
        managed = child.get("is_managed", False)
        tag = " (managed)" if managed else ""
        lines += ["", f"👤 <b>{name}</b>{tag}"]

        tasks = await api_client.get_child_tasks(telegram_id, child["id"])
        if tasks is None:
            lines.append("  ❌ Failed to load tasks")
            continue

        active = [t for t in tasks if t.get("status") != "done"]
        if not active:
            lines.append("  ✅ No active tasks")
        else:
            for t in active:
                emoji = STATUS_EMOJI.get(t.get("status", ""), "•")
                lines.append(f"  {emoji} #{t['id']} {t['title']}")

    lines += ["", "Use /done &lt;id&gt; to complete a task."]
    await message.answer("\n".join(lines), parse_mode="HTML")
