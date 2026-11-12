
from __future__ import annotations

import asyncio
import uuid
from pathlib import Path

import yt_dlp


def _download_facebook(url: str, download_dir: Path) -> Path:
    download_dir.mkdir(parents=True, exist_ok=True)

    download_id = uuid.uuid4().hex

    options = {
        "format": "best[ext=mp4]/best",
        "outtmpl": str(
            download_dir / f"{download_id}_%(id)s.%(ext)s"
        ),
        "noplaylist": True,
        "quiet": True,
        "no_warnings": True,
        "merge_output_format": "mp4",
    }

    with yt_dlp.YoutubeDL(options) as ydl:
        info = ydl.extract_info(url, download=True)
        video_path = Path(ydl.prepare_filename(info))

    if not video_path.exists():
        mp4_path = video_path.with_suffix(".mp4")

        if mp4_path.exists():
            video_path = mp4_path
        else:
            candidates = [
                path
                for path in download_dir.glob(f"{download_id}_*")
                if path.is_file()
                and path.suffix.lower() not in (
                    ".part",
                    ".ytdl",
                    ".temp",
                )
            ]

            if not candidates:
                raise FileNotFoundError(
                    "Downloaded Facebook video was not found"
                )

            video_path = candidates[0]

    return video_path


async def download_facebook_video(
    url: str,
    download_dir: Path,
) -> Path:
    return await asyncio.to_thread(
        _download_facebook,
        url,
        download_dir,
    )
