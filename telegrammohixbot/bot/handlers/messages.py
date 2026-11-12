
from aiogram import Router, F
from aiogram.types import Message

from bot.services.analyzer import detect_platform, is_valid_url
from bot.keyboards.video_menu import build_video_menu_keyboard
from bot.services.url_storage import store_url


router = Router()


@router.message(F.text)
async def handle_text_message(message: Message) -> None:
    text = (message.text or "").strip()

    if not is_valid_url(text):
        await message.reply(
            "سلام! به ربات آذر خوش آمدید 🎬\n\n"
            "لطفاً یک لینک معتبر از یکی از این پلتفرم‌ها بفرستید:\n"
            "YouTube, Instagram, TikTok, Facebook"
        )
        return

    platform = detect_platform(text)

    if platform is None:
        await message.reply(
            "این لینک متعلق به پلتفرم‌های پشتیبانی‌شده نیست.\n"
            "لطفاً لینک YouTube، Instagram، TikTok یا Facebook را بفرستید."
        )
        return

    store_url(
        message.chat.id,
        text,
        message.message_id,
    )

    keyboard = build_video_menu_keyboard()

    await message.reply(
        f"لینک {platform.value} دریافت شد.\n"
        "برای ادامه یکی از گزینه‌های زیر را انتخاب کنید:",
        reply_markup=keyboard,
    )
