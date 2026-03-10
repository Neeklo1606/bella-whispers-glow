"""
Telegram Bot entry point.
"""
import asyncio
import logging
import httpx
from aiogram import Bot, Dispatcher
from aiogram.client.default import DefaultBotProperties
from aiogram.enums import ParseMode

from .handlers import register_handlers
from .middlewares import register_middlewares
from .utils.config import get_bot_config
from .utils.runtime_settings import start_refresh_loop

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

_DEFAULT_TOKEN = "8716981874:AAE2hzfIx8Gk0syIGwmp0ZzP36TRO9CtR8g"


async def _fetch_token_from_api() -> str:
    """Fetch bot token from backend API (localhost only)."""
    config = get_bot_config()
    url = f"{config.API_BASE_URL.rstrip('/')}/api/bot/config"
    try:
        async with httpx.AsyncClient(timeout=10.0) as client:
            r = await client.get(url)
            if r.status_code == 200:
                data = r.json()
                t = data.get("bot_token", "").strip()
                if t:
                    return t
    except Exception as e:
        logger.warning("Failed to fetch token from API: %s", e)
    return ""


async def main():
    """Main bot function."""
    config = get_bot_config()
    start_refresh_loop()  # Fetch MINIAPP_URL, OFFER_URL, SUPPORT_USERNAME from API every 5 min
    token = config.BOT_TOKEN or ""
    if not token:
        token = await _fetch_token_from_api()
    if not token:
        token = _DEFAULT_TOKEN
        logger.info("Using default bot token")
    if not token:
        logger.warning("BOT_TOKEN not set - waiting. Configure via admin panel.")
        while True:
            await asyncio.sleep(60)

    # Initialize bot and dispatcher
    bot = Bot(
        token=token,
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
