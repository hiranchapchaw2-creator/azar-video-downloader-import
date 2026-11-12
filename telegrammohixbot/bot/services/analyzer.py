
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

    options: dict[str, Any] = {
        "format": (
            "bestvideo[ext=mp4]+bestaudio[ext=m4a]"
            "/best[ext=mp4]/best"
        ),
        "merge_output_format": "mp4",
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
            "X download finished but output file was not found"
        )

    mp4_files = [
        path for path in downloaded_files
        if path.suffix.lower() == ".mp4"
    ]

    video_path = mp4_files[0] if mp4_files else downloaded_files[0]

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
