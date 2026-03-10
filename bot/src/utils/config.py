"""
Bot configuration.
"""
from pydantic_settings import BaseSettings


class BotConfig(BaseSettings):
    """Bot configuration."""

    BOT_TOKEN: str = ""
    API_BASE_URL: str = "http://localhost:8000"
    MINIAPP_URL: str = "https://app.bellahasias.ru"
    CHANNEL_ID: str = ""
    BOT_API_SECRET: str = ""
    OFFER_URL: str = "https://app.bellahasias.ru/privacy"
    SUPPORT_USERNAME: str = "Bella_hasias"

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"


def get_bot_config() -> BotConfig:
    """Get bot configuration."""
    return BotConfig()
