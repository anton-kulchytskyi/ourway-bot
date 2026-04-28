"""
HTTP client for ourway-backend API.
Stores per-user JWT tokens in memory (telegram_id → token).
"""
import logging
import time
from typing import Any

import aiohttp

from config import API_URL, BOT_TOKEN

logger = logging.getLogger(__name__)

# In-memory token storage: telegram_id → access_token
_tokens: dict[int, str] = {}
# When each token was saved (unix timestamp): telegram_id → float
_token_saved_at: dict[int, float] = {}
# In-memory locale cache: telegram_id → locale ("en" or "uk")
_locales: dict[int, str] = {}
# In-memory role cache: telegram_id → role ("owner" | "member" | "child")
_roles: dict[int, str] = {}

# Refresh token after 20 hours (access token TTL is 1 day)
_TOKEN_REFRESH_AFTER = 20 * 3600


def save_token(telegram_id: int, token: str) -> None:
    _tokens[telegram_id] = token
    _token_saved_at[telegram_id] = time.time()


def get_token(telegram_id: int) -> str | None:
    return _tokens.get(telegram_id)


def save_locale(telegram_id: int, locale: str) -> None:
    _locales[telegram_id] = locale if locale in ("en", "uk") else "en"


def get_locale(telegram_id: int) -> str:
    return _locales.get(telegram_id, "en")


def save_role(telegram_id: int, role: str) -> None:
    _roles[telegram_id] = role


def get_role(telegram_id: int) -> str | None:
    return _roles.get(telegram_id)


def _auth_headers(telegram_id: int) -> dict[str, str]:
    token = get_token(telegram_id)
    if not token:
        raise ValueError(f"No token for telegram_id={telegram_id}")
    return {"Authorization": f"Bearer {token}"}


def _token_is_stale(telegram_id: int) -> bool:
    saved_at = _token_saved_at.get(telegram_id, 0)
    return (time.time() - saved_at) > _TOKEN_REFRESH_AFTER


async def ensure_token(telegram_id: int) -> bool:
    """Return True if the user has a valid token.

    Proactively refreshes via bot_login when token is missing or older than
    _TOKEN_REFRESH_AFTER seconds, so expired tokens don't cause 401 errors.
    Returns False only when the user is genuinely unregistered.
    """
    if get_token(telegram_id) and not _token_is_stale(telegram_id):
        return True
    result = await bot_login(telegram_id)
    if result and result.get("access_token"):
        save_token(telegram_id, result["access_token"])
        # Restore locale and role from backend if not cached
        if telegram_id not in _locales or telegram_id not in _roles:
            me = await get_me(telegram_id)
            if me:
                save_locale(telegram_id, me.get("locale", "en"))
                save_role(telegram_id, me.get("role", "member"))
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
    """Make an API request. Returns parsed JSON, True for empty 2xx (e.g. 204), or None on error."""
    url = f"{API_URL}{API_PREFIX}{path}"
    async with aiohttp.ClientSession() as session:
        async with session.request(
            method, url, headers=headers, json=json, params=params
        ) as resp:
            if resp.status >= 400:
                body = await resp.text()
                logger.error("API %s %s → %s: %s", method, path, resp.status, body)
                return None
            if resp.status == 204 or resp.content_length == 0:
                return True
            return await resp.json()


# ── Auth ──────────────────────────────────────────────────────────────────────

async def bot_login(telegram_id: int) -> dict | None:
    """Authenticate via telegram_id (requires bot_secret header). Returns tokens or None."""
    return await _request(
        "POST", "/auth/bot-login",
        json={"telegram_id": telegram_id},
        headers={"X-Bot-Secret": BOT_TOKEN},
    )


async def telegram_register(telegram_id: int, name: str, locale: str = "en") -> dict | None:
    """Register a new user directly via Telegram. Returns tokens or None."""
    return await _request(
        "POST", "/auth/telegram-register",
        json={"telegram_id": telegram_id, "name": name, "locale": locale},
        headers={"X-Bot-Secret": BOT_TOKEN},
    )


async def get_web_token(telegram_id: int) -> str | None:
    """Get a short-lived web login token for the user. Returns the token string or None."""
    result = await _request(
        "POST", "/auth/web-token",
        json={"telegram_id": telegram_id},
        headers={"X-Bot-Secret": BOT_TOKEN},
    )
    return result["token"] if result else None


async def link_telegram(link_token: str, telegram_id: int) -> dict | None:
    """Link a telegram_id to an existing account using the deep-link token from bot-create."""
    return await _request(
        "POST", "/users/telegram/link",
        json={"token": link_token, "telegram_id": telegram_id},
    )


# ── Users ─────────────────────────────────────────────────────────────────────


async def get_me(telegram_id: int) -> dict | None:
    return await _request("GET", "/users/me", headers=_auth_headers(telegram_id))


async def update_me(telegram_id: int, **fields) -> dict | None:
    return await _request(
        "PATCH", "/users/me",
        headers=_auth_headers(telegram_id),
        json={k: v for k, v in fields.items()},
    )


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
    assignee_id: int | None = None,
) -> dict | None:
    body: dict = {"title": title, "space_id": space_id, "status": "todo"}
    if scheduled_date:
        body["scheduled_date"] = scheduled_date
    if due_date:
        body["due_date"] = due_date
    if assignee_id is not None:
        body["assignee_id"] = assignee_id
    return await _request("POST", "/tasks", headers=_auth_headers(telegram_id), json=body)


async def complete_task(telegram_id: int, task_id: int) -> dict | None:
    return await _request(
        "PATCH", f"/tasks/{task_id}",
        headers=_auth_headers(telegram_id),
        json={"status": "done"},
    )


async def request_task_done(telegram_id: int, task_id: int) -> dict | None:
    """Child requests parent approval to mark task as done."""
    return await _request(
        "POST", f"/tasks/{task_id}/request_done",
        headers=_auth_headers(telegram_id),
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


async def create_invitation(telegram_id: int, space_id: int | None = None, role: str = "editor") -> dict | None:
    body: dict = {"role": role}
    if space_id is not None:
        body["space_id"] = space_id
    return await _request(
        "POST", "/invitations",
        headers=_auth_headers(telegram_id),
        json=body,
    )


async def accept_invitation(telegram_id: int, token: str) -> bool:
    result = await _request(
        "POST", f"/invitations/{token}/accept",
        headers=_auth_headers(telegram_id),
    )
    return result is not None


async def get_invitation_info(token: str) -> dict | None:
    return await _request("GET", f"/invitations/{token}")


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
    result = await _request("DELETE", f"/schedule/{schedule_id}", headers=_auth_headers(telegram_id))
    return result is not None


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


# ── Events ────────────────────────────────────────────────────────────────────

async def get_events(telegram_id: int, date: str | None = None) -> list | None:
    """Return org events. Children only see events they participate in (enforced by backend)."""
    params = {"date": date} if date else None
    return await _request(
        "GET", "/events",
        headers=_auth_headers(telegram_id),
        params=params,
    )


async def create_event(telegram_id: int, body: dict) -> dict | None:
    """body: {title, date?, time_start?, time_end?, participants?}"""
    return await _request(
        "POST", "/events",
        headers=_auth_headers(telegram_id),
        json=body,
    )


async def delete_event(telegram_id: int, event_id: int) -> bool:
    """Returns True on success (204), False on error."""
    result = await _request(
        "DELETE", f"/events/{event_id}",
        headers=_auth_headers(telegram_id),
    )
    return result is not None
