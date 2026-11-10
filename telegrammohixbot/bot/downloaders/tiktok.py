
from __future__ import annotations

import asyncio
from pathlib import Path

import yt_dlp


def _download_tiktok(url: str, download_dir: Path) -> Path:
    download_dir.mkdir(parents=True, exist_ok=True)

    options = {
        "format": "best[ext=mp4]/best",
        "outtmpl": str(download_dir / "%(id)s.%(ext)s"),
        "noplaylist": True,
        "quiet": True,
        "no_warnings": True,
        "merge_output_format": "mp4",
    }

    with yt_dlp.YoutubeDL(options) as ydl:
        info = ydl.extract_info(url, download=True)
        video_path = Path(ydl.prepare_filename(info))

        if not video_path.exists():
            video_path = video_path.with_suffix(".mp4")

    if not video_path.exists():
        raise FileNotFoundError(
            "Downloaded TikTok video was not found"
        )

    return video_path


async def download_tiktok_video(
    url: str,
    download_dir: Path,
) -> Path:
    return await asyncio.to_thread(
        _download_tiktok,
        url,
        download_dir,
    )
