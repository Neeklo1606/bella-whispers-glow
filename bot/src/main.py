"""
Telegram Bot entry point.
"""
import asyncio
import logging
from aiogram import Bot, Dispatcher
from aiogram.client.default import DefaultBotProperties
from aiogram.enums import ParseMode

from .handlers import register_handlers
from .middlewares import register_middlewares
from .utils.config import get_bot_config
from .utils.runtime_settings import start_refresh_loop

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


async def main():
    """Main bot function."""
    config = get_bot_config()
    start_refresh_loop()  # Fetch MINIAPP_URL, OFFER_URL, SUPPORT_USERNAME from API every 5 min
    if not config.BOT_TOKEN:
        logger.warning("BOT_TOKEN not set - waiting. Configure via admin panel.")
        while True:
            await asyncio.sleep(60)

    # Initialize bot and dispatcher
    bot = Bot(
        token=config.BOT_TOKEN,
        default=DefaultBotProperties(parse_mode=ParseMode.HTML)
    )
    dp = Dispatcher()

    # Register middlewares
    register_middlewares(dp)

    # Register handlers
    register_handlers(dp)

    # Start polling
    logger.info("Bot started")
    await dp.start_polling(bot)


if __name__ == "__main__":
    asyncio.run(main())
