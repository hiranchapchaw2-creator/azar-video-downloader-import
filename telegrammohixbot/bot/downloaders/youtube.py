
"""
YouTube and YouTube Shorts downloader using yt-dlp.
"""

from __future__ import annotations

import asyncio
import uuid
from pathlib import Path
from typing import Any

from yt_dlp import YoutubeDL

from bot.utils.cleaner import safe_unlink
from bot.utils.logger import get_logger


logger = get_logger()


def _build_ydl_opts(
    download_dir: Path,
    download_id: str,
) -> dict[str, Any]:
    return {
        "format": (
            "bestvideo[ext=mp4]+bestaudio[ext=m4a]"
            "/best[ext=mp4]/best"
        ),
        "merge_output_format": "mp4",
        "outtmpl": str(
            download_dir / f"{download_id}_%(id)s.%(ext)s"
        ),
        "restrictfilenames": True,
        "noplaylist": True,
        "quiet": True,
        "no_warnings": True,
    }


def _find_downloaded_file(
    info: dict[str, Any],
    download_dir: Path,
    download_id: str,
    ydl: YoutubeDL,
) -> Path:
    possible_paths: list[Path] = []

    filepath = info.get("filepath")
    if filepath:
        possible_paths.append(Path(filepath))

    requested_downloads = info.get("requested_downloads") or []
    for item in requested_downloads:
        filepath = item.get("filepath")
        if filepath:
            possible_paths.append(Path(filepath))

    prepared_path = Path(ydl.prepare_filename(info))
    possible_paths.append(prepared_path)

    for path in possible_paths:
        if path.is_file():
            return path

        mp4_path = path.with_suffix(".mp4")
        if mp4_path.is_file():
            return mp4_path

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

    mp4_files = [
        path for path in candidates
        if path.suffix.lower() == ".mp4"
    ]

    if len(mp4_files) == 1:
        return mp4_files[0]

    if len(mp4_files) > 1:
        raise RuntimeError(
            "Multiple MP4 output files found for one YouTube download"
        )

    if len(candidates) == 1:
        return candidates[0]

    if not candidates:
        raise FileNotFoundError(
            "YouTube download finished but output file was not found"
        )

    raise RuntimeError(
        "Could not identify a unique YouTube output file"
    )


def _download_sync(url: str, download_dir: Path) -> Path:
    download_id = uuid.uuid4().hex
    ydl_opts = _build_ydl_opts(download_dir, download_id)

    logger.info("Starting YouTube download")

    try:
        with YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(url, download=True)

            if not info:
                raise ValueError(
                    "YouTube video information could not be extracted"
                )

            downloaded_file = _find_downloaded_file(
                info,
                download_dir,
                download_id,
                ydl,
            )

        logger.info(
            "YouTube download finished: %s",
            downloaded_file,
        )

        return downloaded_file

    except Exception:
        logger.exception("YouTube download failed")

        for path in download_dir.glob(f"{download_id}_*"):
            if path.is_file():
                safe_unlink(path)

        raise


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
