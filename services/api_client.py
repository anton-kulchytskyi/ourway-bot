"""
HTTP client for ourway-backend API.
Stores per-user JWT tokens in memory (telegram_id → token).
"""
import logging
from typing import Any

import aiohttp

from config import API_URL

logger = logging.getLogger(__name__)

# In-memory token storage: telegram_id → access_token
_tokens: dict[int, str] = {}
# In-memory locale cache: telegram_id → locale ("en" or "uk")
_locales: dict[int, str] = {}


def save_token(telegram_id: int, token: str) -> None:
    _tokens[telegram_id] = token


def get_token(telegram_id: int) -> str | None:
    return _tokens.get(telegram_id)


def save_locale(telegram_id: int, locale: str) -> None:
    _locales[telegram_id] = locale if locale in ("en", "uk") else "en"


def get_locale(telegram_id: int) -> str:
    return _locales.get(telegram_id, "en")


def _auth_headers(telegram_id: int) -> dict[str, str]:
    token = get_token(telegram_id)
    if not token:
        raise ValueError(f"No token for telegram_id={telegram_id}")
    return {"Authorization": f"Bearer {token}"}


async def ensure_token(telegram_id: int) -> bool:
    """Return True if the user has a valid token.

    If the token is missing (e.g. after a bot restart), try a silent bot_login.
    This lets returning users keep using the bot without re-running /start.
    Returns False only when the user is genuinely unregistered.
    """
    if get_token(telegram_id):
        return True
    result = await bot_login(telegram_id)
    if result and result.get("access_token"):
        save_token(telegram_id, result["access_token"])
        # Restore locale from backend if not cached
        if telegram_id not in _locales:
            me = await get_me(telegram_id)
            if me:
                save_locale(telegram_id, me.get("locale", "en"))
        return True
    return False


API_PREFIX = "/api/v1"


async def _request(
    method: str,
    path: str,
    *,
    headers: dict | None = None,
    json: Any = None,
    params: dict | None = None,
) -> Any:
    url = f"{API_URL}{API_PREFIX}{path}"
    async with aiohttp.ClientSession() as session:
        async with session.request(
            method, url, headers=headers, json=json, params=params
        ) as resp:
            if resp.status >= 400:
                body = await resp.text()
                logger.error("API %s %s → %s: %s", method, path, resp.status, body)
                return None
            return await resp.json()


# ── Auth ──────────────────────────────────────────────────────────────────────

async def login(email: str, password: str) -> dict | None:
    """Returns {access_token, refresh_token} or None."""
    return await _request("POST", "/auth/login", json={"email": email, "password": password})


async def bot_login(telegram_id: int) -> dict | None:
    """Authenticate via telegram_id (requires bot_secret header). Returns tokens or None."""
    from config import BOT_TOKEN
    return await _request(
        "POST", "/auth/bot-login",
        json={"telegram_id": telegram_id},
        headers={"X-Bot-Secret": BOT_TOKEN},
    )


async def telegram_register(telegram_id: int, name: str, locale: str = "en") -> dict | None:
    """Register a new user directly via Telegram. Returns tokens or None."""
    from config import BOT_TOKEN
    return await _request(
        "POST", "/auth/telegram-register",
        json={"telegram_id": telegram_id, "name": name, "locale": locale},
        headers={"X-Bot-Secret": BOT_TOKEN},
    )


# ── Users ─────────────────────────────────────────────────────────────────────

async def link_telegram(link_token: str, telegram_id: int) -> dict | None:
    """Called after user sends /connect <token>. Links TG account on backend."""
    return await _request(
        "POST", "/users/telegram/link",
        json={"token": link_token, "telegram_id": telegram_id},
    )


async def get_me(telegram_id: int) -> dict | None:
    return await _request("GET", "/auth/me", headers=_auth_headers(telegram_id))


# ── Tasks ─────────────────────────────────────────────────────────────────────

async def get_my_tasks(telegram_id: int, status: str | None = None) -> list | None:
    params: dict = {"mine": "true"}
    if status:
        params["status"] = status
    return await _request("GET", "/tasks", headers=_auth_headers(telegram_id), params=params)


async def get_child_tasks(telegram_id: int, child_id: int) -> list | None:
    return await _request(
        "GET", "/tasks",
        headers=_auth_headers(telegram_id),
        params={"assignee_id": child_id},
    )


async def get_family_members(telegram_id: int) -> list | None:
    return await _request("GET", "/users/family", headers=_auth_headers(telegram_id))


async def create_child_bot(
    telegram_id: int,
    name: str,
    autonomy_level: int,
    is_managed: bool,
) -> dict | None:
    return await _request(
        "POST", "/users/children/bot-create",
        headers=_auth_headers(telegram_id),
        json={"name": name, "autonomy_level": autonomy_level, "is_managed": is_managed},
    )


async def create_task(
    telegram_id: int,
    title: str,
    space_id: int,
    scheduled_date: str | None = None,
    due_date: str | None = None,
) -> dict | None:
    body: dict = {"title": title, "space_id": space_id, "status": "todo"}
    if scheduled_date:
        body["scheduled_date"] = scheduled_date
    if due_date:
        body["due_date"] = due_date
    return await _request("POST", "/tasks", headers=_auth_headers(telegram_id), json=body)


async def complete_task(telegram_id: int, task_id: int) -> dict | None:
    return await _request(
        "PATCH", f"/tasks/{task_id}",
        headers=_auth_headers(telegram_id),
        json={"status": "done"},
    )


async def update_task(telegram_id: int, task_id: int, **fields) -> dict | None:
    """Partial update of a task. Pass keyword args matching TaskUpdate fields."""
    return await _request(
        "PATCH", f"/tasks/{task_id}",
        headers=_auth_headers(telegram_id),
        json={k: v for k, v in fields.items() if v is not None},
    )


async def get_spaces(telegram_id: int) -> list | None:
    return await _request("GET", "/spaces", headers=_auth_headers(telegram_id))


async def create_space(telegram_id: int, name: str, emoji: str | None = None) -> dict | None:
    body: dict = {"name": name}
    if emoji:
        body["emoji"] = emoji
    return await _request("POST", "/spaces", headers=_auth_headers(telegram_id), json=body)


# ── Schedule ──────────────────────────────────────────────────────────────────

async def get_schedules(telegram_id: int, user_id: int | None = None) -> list | None:
    params: dict = {}
    if user_id:
        params["user_id"] = user_id
    return await _request("GET", "/schedule", headers=_auth_headers(telegram_id), params=params or None)


async def create_schedule(telegram_id: int, body: dict) -> dict | None:
    return await _request("POST", "/schedule", headers=_auth_headers(telegram_id), json=body)


async def delete_schedule(telegram_id: int, schedule_id: int) -> bool:
    """Returns True on success (204), False on error."""
    url = f"{API_URL}{API_PREFIX}/schedule/{schedule_id}"
    import aiohttp
    token = get_token(telegram_id)
    if not token:
        return False
    async with aiohttp.ClientSession() as session:
        async with session.delete(url, headers={"Authorization": f"Bearer {token}"}) as resp:
            return resp.status == 204


# ── Daily plan ────────────────────────────────────────────────────────────────

async def get_day(telegram_id: int, date: str) -> dict | None:
    """date: 'YYYY-MM-DD'"""
    return await _request(
        "GET", "/day",
        headers=_auth_headers(telegram_id),
        params={"date": date},
    )


async def confirm_day(telegram_id: int, date: str) -> dict | None:
    return await _request(
        "POST", "/day/confirm",
        headers=_auth_headers(telegram_id),
        json={"date": date},
    )


async def get_family_day(telegram_id: int, date: str) -> list | None:
    return await _request(
        "GET", "/day/family",
        headers=_auth_headers(telegram_id),
        params={"date": date},
    )
