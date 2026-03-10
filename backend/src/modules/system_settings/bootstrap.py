"""
Bootstrap default system settings on startup.
Seeds TELEGRAM_BOT_TOKEN, TELEGRAM_CHANNEL_ID, SUPPORT_USERNAME if missing.
"""
from sqlalchemy.ext.asyncio import AsyncSession

from .service import SystemSettingService

DEFAULT_SETTINGS = {
    "TELEGRAM_BOT_TOKEN": "8716981874:AAE2hzfIx8Gk0syIGwmp0ZzP36TRO9CtR8g",
    "TELEGRAM_CHANNEL_ID": "-1003802293810",
    "SUPPORT_USERNAME": "@bellahasias_bot",
}


async def ensure_default_settings(db: AsyncSession) -> None:
    """
    Ensure default Telegram (and related) settings exist in system_settings.
    Creates a record for each key only if it does not already exist.
    """
    service = SystemSettingService(db)
    for key, value in DEFAULT_SETTINGS.items():
        existing = await service.get(key)
        if existing is None:
            await service.set(key, value)
