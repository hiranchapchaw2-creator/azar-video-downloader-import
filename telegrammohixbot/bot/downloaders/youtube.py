
"""
YouTube and YouTube Shorts downloader using yt-dlp.
"""

from __future__ import annotations

import asyncio
import uuid
from pathlib import Path
from typing import Any

from yt_dlp import YoutubeDL

from bot.utils.logger import get_logger


logger = get_logger()


def _build_ydl_opts(download_dir: Path, download_id: str) -> dict[str, Any]:
    return {
        "format": (
            "bestvideo[ext=mp4]+bestaudio[ext=m4a]"
            "/best[ext=mp4]/best"
        ),
        "merge_output_format": "mp4",
        "outtmpl": str(
            download_dir / f"{download_id}_%(title).80s.%(ext)s"
        ),
        "restrictfilenames": True,
        "noplaylist": True,
        "quiet": True,
        "no_warnings": True,
    }


def _download_sync(url: str, download_dir: Path) -> Path:
    download_id = uuid.uuid4().hex
    ydl_opts = _build_ydl_opts(download_dir, download_id)

    logger.info("Starting YouTube download")

    with YoutubeDL(ydl_opts) as ydl:
        ydl.download([url])

    downloaded_files = [
        path
        for path in download_dir.glob(f"{download_id}_*")
        if path.is_file()
        and path.suffix.lower() not in (".part", ".ytdl", ".temp")
    ]

    if not downloaded_files:
        raise FileNotFoundError(
            "YouTube download finished but output file was not found"
        )

    mp4_files = [
        path for path in downloaded_files
        if path.suffix.lower() == ".mp4"
    ]

    downloaded_file = (
        mp4_files[0] if mp4_files else downloaded_files[0]
    )

    logger.info("YouTube download finished: %s", downloaded_file)

    return downloaded_file


async def download_youtube_video(
    url: str,
    download_dir: Path,
) -> Path:
    download_dir.mkdir(parents=True, exist_ok=True)

    return await asyncio.to_thread(
        _download_sync,
        url,
        download_dir,
    )
