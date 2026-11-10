
"""
Async download queue and worker.
"""

from __future__ import annotations

import asyncio
from dataclasses import dataclass
from pathlib import Path
from typing import Optional

from aiogram import Bot

from bot.services.analyzer import Platform
from bot.services.uploader import upload_video_flow

from bot.downloaders.youtube import download_youtube_video
from bot.downloaders.instagram import download_instagram_video
from bot.downloaders.tiktok import download_tiktok_video
from bot.downloaders.facebook import download_facebook_video

from bot.utils.cleaner import ensure_download_dir
from bot.utils.logger import get_logger


logger = get_logger()


@dataclass
class DownloadTask:
    url: str
    platform: Platform
    chat_id: int
    status_message_id: int
    original_message_id: int


class DownloadQueue:
    """Sequential asynchronous download queue."""

    def __init__(self) -> None:
        self._queue: asyncio.Queue[DownloadTask] = asyncio.Queue()
        self._worker_task: Optional[asyncio.Task] = None

    async def enqueue(self, task: DownloadTask) -> None:
        logger.info("Enqueuing task: %s", task)
        await self._queue.put(task)

    def start_worker(self, bot: Bot) -> asyncio.Task:
        if self._worker_task is None or self._worker_task.done():
            self._worker_task = asyncio.create_task(
                self._worker_loop(bot),
                name="download-worker",
            )
        return self._worker_task

    async def _worker_loop(self, bot: Bot) -> None:
        download_dir = ensure_download_dir()
        logger.info("Download worker started: %s", download_dir)

        while True:
            task = await self._queue.get()

            try:
                await bot.edit_message_text(
                    chat_id=task.chat_id,
                    message_id=task.status_message_id,
                    text="⏳ Downloading...",
                )

                video_path = await self._download_video(
                    task, download_dir
                )

                await bot.edit_message_text(
                    chat_id=task.chat_id,
                    message_id=task.status_message_id,
                    text="✅ Download complete\n📤 Uploading to Telegram...",
                )

                await upload_video_flow(
                    bot=bot,
                    chat_id=task.chat_id,
                    video_path=video_path,
                    status_message_id=task.status_message_id,
                    reply_to_message_id=task.original_message_id,
                )

            except Exception as exc:
                logger.exception(
                    "Error while processing task: %s", task
                )

                try:
                    await bot.edit_message_text(
                        chat_id=task.chat_id,
                        message_id=task.status_message_id,
                        text=f"An error occurred: {exc}",
                    )
                except Exception:
                    logger.exception("Failed to notify user")

            finally:
                self._queue.task_done()

    async def _download_video(
        self,
        task: DownloadTask,
        download_dir: Path,
    ) -> Path:

        if task.platform is Platform.YOUTUBE:
            return await download_youtube_video(
                task.url, download_dir
            )

        if task.platform is Platform.INSTAGRAM:
            return await download_instagram_video(
                task.url, download_dir
            )

        if task.platform is Platform.TIKTOK:
            return await download_tiktok_video(
                task.url, download_dir
            )

        if task.platform is Platform.FACEBOOK:
            return await download_facebook_video(
                task.url, download_dir
            )

        raise ValueError(
            f"Unsupported platform: {task.platform}"
        )


download_queue = DownloadQueue()
