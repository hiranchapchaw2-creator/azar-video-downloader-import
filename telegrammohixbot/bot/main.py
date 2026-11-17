
import asyncio
import os
import contextlib
from pathlib import Path

from aiogram import Bot, Dispatcher

from bot.handlers.start import router as start_router
from bot.handlers.messages import router as messages_router
from bot.handlers.callbacks import router as callbacks_router
from bot.services.queue import download_queue
from bot.utils.logger import setup_logger


BASE_DIR = Path(__file__).resolve().parent.parent
TOKEN_FILE = BASE_DIR / "api_key_bot.txt"


def load_bot_token() -> str:
    """Load the Telegram bot token from the environment or token file."""

    token = os.getenv("BOT_TOKEN", "").strip()

    if not token and TOKEN_FILE.exists():
        token = TOKEN_FILE.read_text(encoding="utf-8").strip()

    if not token:
        raise RuntimeError(
            "Bot token not found or empty. "
            "Set BOT_TOKEN or add a valid token to api_key_bot.txt."
        )

    return token


async def main() -> None:
    logger = setup_logger()

    token = load_bot_token()
    bot = Bot(token=token)
    dp = Dispatcher()

    dp.include_router(start_router)
    dp.include_router(messages_router)
    dp.include_router(callbacks_router)

    worker_task = download_queue.start_worker(bot=bot)
    logger.info("Background download worker started")

    try:
        logger.info("Starting bot polling")
        await dp.start_polling(bot)
    finally:
        logger.info("Shutting down...")

        worker_task.cancel()

        with contextlib.suppress(asyncio.CancelledError):
            await worker_task

        await bot.session.close()


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except (KeyboardInterrupt, SystemExit):
        pass
