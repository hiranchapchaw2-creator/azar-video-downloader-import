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
    token = os.getenv("BOT_TOKEN")
    if token:
        return token.strip()

    if TOKEN_FILE.exists():
        return TOKEN_FILE.read_text(encoding="utf-8").strip()

    raise RuntimeError(
        "Bot token not found. Set BOT_TOKEN environment variable."
    )


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
