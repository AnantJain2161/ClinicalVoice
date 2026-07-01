import json
from typing import Any

import redis

from app.config import settings

_client: redis.Redis | None = None

SESSION_TTL_SECONDS = 60 * 60  # 1 hour of inactivity before a session expires


def get_client() -> redis.Redis:
    global _client
    if _client is None:
        _client = redis.from_url(settings.redis_url, decode_responses=True)
    return _client


def _session_key(session_id: str) -> str:
    return f"session:{session_id}"


def set_session_state(session_id: str, state: dict[str, Any], ttl_seconds: int = SESSION_TTL_SECONDS) -> None:
    get_client().set(_session_key(session_id), json.dumps(state), ex=ttl_seconds)


def get_session_state(session_id: str) -> dict[str, Any] | None:
    raw = get_client().get(_session_key(session_id))
    return json.loads(raw) if raw is not None else None


def delete_session_state(session_id: str) -> None:
    get_client().delete(_session_key(session_id))
