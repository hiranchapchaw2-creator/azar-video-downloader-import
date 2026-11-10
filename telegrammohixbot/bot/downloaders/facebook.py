
from __future__ import annotations

import asyncio
from pathlib import Path

import yt_dlp


def _download_facebook(url: str, download_dir: Path) -> Path:
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

        video_id = info.get("id")
        video_path = Path(ydl.prepare_filename(info))

        if video_path.exists():
            return video_path

        if video_id:
            candidates = [
                path for path in download_dir.glob(f"{video_id}.*")
                if path.suffix not in (".part", ".ytdl")
            ]

            if candidates:
                return candidates[0]

    raise FileNotFoundError(
        "Downloaded Facebook video was not found"
    )


async def download_facebook_video(
    url: str,
    download_dir: Path,
) -> Path:
    return await asyncio.to_thread(
        _download_facebook,
        url,
        download_dir,
    )
