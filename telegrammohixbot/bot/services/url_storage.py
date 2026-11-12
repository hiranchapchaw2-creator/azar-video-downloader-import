from __future__ import annotations

from dataclasses import dataclass
from typing import Optional


@dataclass
class UserSession:
    url: str
    message_id: int


user_sessions: dict[int, UserSession] = {}


def store_url(
    chat_id: int,
    url: str,
    message_id: int,
) -> None:
    user_sessions[chat_id] = UserSession(
        url=url,
        message_id=message_id,
    )


def get_url(chat_id: int) -> Optional[str]:
    session = user_sessions.get(chat_id)
    return session.url if session else None


def get_message_id(chat_id: int) -> Optional[int]:
    session = user_sessions.get(chat_id)
    return session.message_id if session else None


def clear_url(chat_id: int) -> None:
    user_sessions.pop(chat_id, None)


def has_url(chat_id: int) -> bool:
    return chat_id in user_sessions
