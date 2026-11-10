"""
Handlers for the /start command and its inline buttons.
"""

from __future__ import annotations

from aiogram import Router, F
from aiogram.filters import CommandStart
from aiogram.types import CallbackQuery, Message

from bot.keyboards.start_keyboard import (
    StartCallbacks,
    build_start_keyboard,
)


router = Router()


START_MESSAGE = (
    "👋 Welcome to Azar Video Bot!\n\n"
    "This bot supports video downloads from:\n\n"
    "• YouTube Videos and Shorts\n"
    "• Instagram Reels and Videos\n"
    "• TikTok Videos\n"
    "• Facebook Videos\n\n"
    "Send a video link to get started. 🎬"
)


@router.message(CommandStart())
async def handle_start(message: Message) -> None:
    await message.answer(
        START_MESSAGE,
        reply_markup=build_start_keyboard(),
    )


@router.callback_query(F.data == StartCallbacks.DOWNLOAD)
async def handle_start_download_button(
    callback: CallbackQuery,
) -> None:
    if callback.message is not None:
        await callback.message.edit_text(
            "📥 Please send a video link from one of these platforms:\n\n"
            "• YouTube\n"
            "• Instagram\n"
            "• TikTok\n"
            "• Facebook",
            reply_markup=build_start_keyboard(),
        )

    await callback.answer()


@router.callback_query(F.data == StartCallbacks.HOW_TO_USE)
async def handle_start_how_to_use_button(
    callback: CallbackQuery,
) -> None:
    text = (
        "ℹ️ How to use Azar Video Bot:\n\n"
        "1️⃣ Copy a video link from a supported platform.\n"
        "2️⃣ Send the link here.\n"
        "3️⃣ Press the Download button.\n"
        "4️⃣ Wait for the bot to process and send your video.\n\n"
        "Supported platforms: YouTube, Instagram, TikTok and Facebook."
    )

    if callback.message is not None:
        await callback.message.edit_text(
            text,
            reply_markup=build_start_keyboard(),
        )

    await callback.answer()


@router.callback_query(F.data == StartCallbacks.SUPPORTED)
async def handle_start_supported_button(
    callback: CallbackQuery,
) -> None:
    text = (
        "❓ Supported platforms:\n\n"
        "• YouTube Videos and Shorts\n"
        "• Instagram Reels and Videos\n"
        "• TikTok Videos\n"
        "• Facebook Videos\n\n"
        "Note: Private, restricted or login-protected videos "
        "may not be downloadable."
    )

    if callback.message is not None:
        await callback.message.edit_text(
            text,
            reply_markup=build_start_keyboard(),
        )

    await callback.answer()
