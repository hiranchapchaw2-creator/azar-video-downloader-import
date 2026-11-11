
from __future__ import annotations

from typing import List

TELEGRAM_MAX_MESSAGE_LENGTH = 4096


def split_message(
    text: str,
    max_length: int = TELEGRAM_MAX_MESSAGE_LENGTH,
    prefix: str = "",
) -> List[str]:
    if max_length <= len(prefix):
        raise ValueError("max_length must be greater than prefix length")

    available_length = max_length - len(prefix)

    if not text:
        return [""]

    chunks: List[str] = []

    while len(text) > available_length:
        split_at = text.rfind("\n", 0, available_length + 1)

        if split_at <= 0:
            split_at = text.rfind(" ", 0, available_length + 1)

        if split_at <= 0:
            split_at = available_length
        else:
            split_at += 1

        chunks.append(text[:split_at].rstrip())
        text = text[split_at:].lstrip()

    if text:
        chunks.append(text)

    return chunks
