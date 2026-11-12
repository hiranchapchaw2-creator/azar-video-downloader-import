
from __future__ import annotations

from enum import Enum
from urllib.parse import urlsplit


class Platform(Enum):
    YOUTUBE = "YouTube"
    INSTAGRAM = "Instagram"
    TIKTOK = "TikTok"
    FACEBOOK = "Facebook"


def is_valid_url(url: str) -> bool:
    if not url or not isinstance(url, str):
        return False

    try:
        parsed = urlsplit(url.strip())

        return (
            parsed.scheme in ("http", "https")
            and bool(parsed.hostname)
            and "." in parsed.hostname
        )

    except ValueError:
        return False


def detect_platform(url: str) -> Platform | None:
    if not is_valid_url(url):
        return None

    try:
        hostname = (urlsplit(url.strip()).hostname or "").lower()
    except ValueError:
        return None

    def matches_domain(domain: str) -> bool:
        return (
            hostname == domain
            or hostname.endswith("." + domain)
        )

    if (
        matches_domain("youtube.com")
        or matches_domain("youtu.be")
    ):
        return Platform.YOUTUBE

    if matches_domain("instagram.com"):
        return Platform.INSTAGRAM

    if matches_domain("tiktok.com"):
        return Platform.TIKTOK

    if (
        matches_domain("facebook.com")
        or matches_domain("fb.watch")
        or matches_domain("fb.com")
    ):
        return Platform.FACEBOOK

    return None
