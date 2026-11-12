from __future__ import annotations

from aiogram import Router, F
from aiogram.types import CallbackQuery

from bot.keyboards.video_menu import (
    VideoMenuCallbacks,
    build_video_menu_keyboard,
)
from bot.services.analyzer import detect_platform, is_valid_url, Platform
from bot.services.queue import download_queue, DownloadTask
from bot.services.description_extractor import get_video_description
from bot.services.url_storage import (
    get_url,
    get_message_id,
    clear_url,
    has_url,
)
from bot.utils.message_splitter import split_message
from bot.utils.logger import get_logger


logger = get_logger()
router = Router()


@router.callback_query(F.data == VideoMenuCallbacks.BACK)
async def handle_back(callback: CallbackQuery) -> None:
    if callback.message is None:
        await callback.answer()
        return

    chat_id = callback.message.chat.id

    if not has_url(chat_id):
        await callback.answer(
            "No stored link found. Please send a video link first.",
            show_alert=True,
        )
        return

    await callback.message.edit_text(
        "What would you like to do with this link?",
        reply_markup=build_video_menu_keyboard(),
    )
    await callback.answer("Returned to menu")


@router.callback_query(F.data == VideoMenuCallbacks.CANCEL)
async def handle_cancel(callback: CallbackQuery) -> None:
    if callback.message is None:
        await callback.answer()
        return

    chat_id = callback.message.chat.id
    clear_url(chat_id)

    await callback.message.edit_text(
        "❌ Cancelled.\n\n"
        "Please send a new video link to continue."
    )
    await callback.answer("Cancelled")


@router.callback_query(F.data == VideoMenuCallbacks.DOWNLOAD_VIDEO)
async def handle_download_video(callback: CallbackQuery) -> None:
    if callback.message is None:
        await callback.answer()
        return

    chat_id = callback.message.chat.id
    url = get_url(chat_id)
    original_message_id = get_message_id(chat_id)

    if not url or not is_valid_url(url):
        await callback.answer(
            "No valid stored link found. Please send a video link first.",
            show_alert=True,
        )
        return

    platform = detect_platform(url)

    if platform not in (
        Platform.YOUTUBE,
        Platform.INSTAGRAM,
        Platform.TIKTOK,
        Platform.FACEBOOK,
    ):
        await callback.answer(
            "Unsupported platform.",
            show_alert=True,
        )
        return

    message_id = callback.message.message_id

    try:
        await callback.message.edit_text(
            "⏳ Your video has been added to the download queue."
        )

        task = DownloadTask(
            url=url,
            platform=platform,
            chat_id=chat_id,
            status_message_id=message_id,
            original_message_id=original_message_id,
        )

        await download_queue.enqueue(task)
        await callback.answer("Video added to download queue")

    except Exception:
        logger.exception("Could not enqueue download request")

        await callback.answer(
            "Could not add the video to the queue. Please try again.",
            show_alert=True,
        )


@router.callback_query(F.data == VideoMenuCallbacks.GET_DESCRIPTION)
async def handle_get_description(callback: CallbackQuery) -> None:
    if callback.message is None:
        await callback.answer()
        return

    chat_id = callback.message.chat.id
    url = get_url(chat_id)

    if not url or not is_valid_url(url):
        await callback.answer(
            "No valid stored link found. Please send a video link first.",
            show_alert=True,
        )
        return

    await callback.message.edit_text(
        "⏳ Extracting video description..."
    )
    await callback.answer()

    try:
        description = await get_video_description(url)

        if not description or not description.strip():
            await callback.message.edit_text(
                "❌ Could not extract video description.\n\n"
                "What would you like to do with this link?",
                reply_markup=build_video_menu_keyboard(),
            )
            return

        prefix = "📝 Video Description:\n\n"
        continuation_prefix = (
            "📝 Video Description (continued):\n\n"
        )

        chunks = split_message(
            description,
            prefix=continuation_prefix,
        )

        await callback.message.edit_text(
            f"{prefix}{chunks[0]}"
        )

        for chunk in chunks[1:]:
            await callback.message.answer(
                f"{continuation_prefix}{chunk}"
            )

        await callback.message.answer(
            "What would you like to do with this link?",
            reply_markup=build_video_menu_keyboard(),
        )

    except Exception:
        logger.exception("Error extracting description")

        await callback.message.edit_text(
            "❌ An error occurred while extracting the description.\n\n"
            "What would you like to do with this link?",
            reply_markup=build_video_menu_keyboard(),
        )
