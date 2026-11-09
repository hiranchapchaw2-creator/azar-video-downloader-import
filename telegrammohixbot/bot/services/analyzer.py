
"""
URL analyzer service.

Responsibility:
- Basic validation that a string looks like a URL
- Detection of supported video platforms
"""

from __future__ import annotations

import enum
import re
from typing import Optional
from urllib.parse import urlparse


class Platform(str, enum.Enum):
    """Supported platforms."""

    YOUTUBE = "youtube"
    INSTAGRAM = "instagram"
    TIKTOK = "tiktok"
    FACEBOOK = "facebook"
    X = "x"


_URL_REGEX = re.compile(
    r"^https?://[^\s]+$",
    re.IGNORECASE,
)


def is_valid_url(text: str) -> bool:
    """Return True if the input looks like a valid HTTP/HTTPS URL."""
    text = text.strip()

    if not _URL_REGEX.match(text):
        return False

    try:
        parsed = urlparse(text)
        return bool(parsed.hostname)
    except ValueError:
        return False


def detect_platform(url: str) -> Optional[Platform]:
    """Detect the platform from the exact hostname."""
    try:
        hostname = (urlparse(url.strip()).hostname or "").lower()
    except ValueError:
        return None

    def matches(domain: str) -> bool:
        return hostname == domain or hostname.endswith("." + domain)

    if matches("youtube.com") or matches("youtu.be"):
        return Platform.YOUTUBE

    if matches("instagram.com"):
        return Platform.INSTAGRAM

    if matches("tiktok.com"):
        return Platform.TIKTOK

    if matches("facebook.com") or matches("fb.watch"):
        return Platform.FACEBOOK

    if matches("x.com") or matches("twitter.com"):
        return Platform.X

    return None
