"""
Application configuration settings.
"""
from pydantic_settings import BaseSettings, SettingsConfigDict
from typing import List


class Settings(BaseSettings):
    """Application settings loaded from environment variables."""

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore",
    )

    # Application
    APP_NAME: str = "Bella Subscription Platform"
    APP_VERSION: str = "1.0.0"
    DEBUG: bool = True
    ENVIRONMENT: str = "development"

    # Server
    HOST: str = "0.0.0.0"
    PORT: int = 8000

    # Database
    DATABASE_URL: str
    DATABASE_POOL_SIZE: int = 10
    DATABASE_MAX_OVERFLOW: int = 20

    # Redis
    REDIS_URL: str = "redis://localhost:6379/0"
    REDIS_CACHE_URL: str = "redis://localhost:6379/1"
    REDIS_JOBS_URL: str = "redis://localhost:6379/2"

    # Security
    SECRET_KEY: str  # JWT secret key
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30
    REFRESH_TOKEN_EXPIRE_DAYS: int = 7

    # Telegram (bootstrap only; runtime from system_settings)
    TELEGRAM_BOT_TOKEN: str = ""
    TELEGRAM_CHANNEL_ID: str = ""
    TELEGRAM_WEBHOOK_URL: str = ""
    BOT_API_SECRET: str = ""

    # Payment Provider (defaults used when not set in .env)
    YOOKASSA_SHOP_ID: str = "1294766"
    YOOKASSA_SECRET_KEY: str = "live_dARehpUSwWdmqXUV9q5NNI_ys_hdVqdBzTujqkBfk6U"
    YOOKASSA_TEST_MODE: bool = False

    # CORS
    CORS_ORIGINS: List[str] = ["http://localhost:3000"]
    CORS_ALLOW_CREDENTIALS: bool = True

    # Admin
    ADMIN_EMAIL: str = "admin@example.com"
    ADMIN_PASSWORD: str = ""

    @property
    def database_url_async(self) -> str:
        """Get async database URL."""
        return self.DATABASE_URL.replace("postgresql://", "postgresql+asyncpg://")

    @property
    def cors_origins_list(self) -> List[str]:
        """Parse CORS origins from string."""
        if isinstance(self.CORS_ORIGINS, str):
            return [origin.strip() for origin in self.CORS_ORIGINS.split(",")]
        return self.CORS_ORIGINS


settings = Settings()
