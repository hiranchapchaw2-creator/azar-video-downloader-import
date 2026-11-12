
from __future__ import annotations

import asyncio
import uuid
from pathlib import Path
from typing import Any

from yt_dlp import YoutubeDL

from bot.utils.logger import get_logger


logger = get_logger()


def _download_x_sync(url: str, download_dir: Path) -> Path:
    download_id = uuid.uuid4().hex

    download_dir.mkdir(parents=True, exist_ok=True)

    options: dict[str, Any] = {
        "format": "best[ext=mp4]/best",
        "outtmpl": str(
            download_dir / f"{download_id}_%(id)s.%(ext)s"
        ),
        "noplaylist": True,
        "quiet": True,
        "no_warnings": True,
        "restrictfilenames": True,
    }

    logger.info("Starting X video download")

    with YoutubeDL(options) as ydl:
        ydl.download([url])

    downloaded_files = [
        path
        for path in download_dir.glob(f"{download_id}_*")
        if path.is_file()
        and path.suffix.lower() not in (
            ".part",
            ".ytdl",
            ".temp",
        )
    ]

    if not downloaded_files:
        raise FileNotFoundError(
            "X video download finished but output file was not found"
        )

    video_path = downloaded_files[0]

    logger.info("X video download finished: %s", video_path)

    return video_path


async def download_x_video(
    url: str,
    download_dir: Path,
) -> Path:
    download_dir.mkdir(parents=True, exist_ok=True)

    return await asyncio.to_thread(
        _download_x_sync,
        url,
        download_dir,
    )
