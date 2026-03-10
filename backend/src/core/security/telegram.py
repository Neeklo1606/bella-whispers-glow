"""
Telegram WebApp initData verification.
Uses system_settings for TELEGRAM_BOT_TOKEN, fallback to .env.
"""
import hmac
import hashlib
import urllib.parse
from typing import Dict, Optional
from sqlalchemy.ext.asyncio import AsyncSession

from ...core.config import settings


def parse_init_data(init_data: str) -> Dict[str, str]:
    """
    Parse Telegram WebApp initData string.
    
    Args:
        init_data: Raw initData string from Telegram WebApp
        
    Returns:
        Dictionary of parsed key-value pairs
    """
    parsed = {}
    for pair in init_data.split("&"):
        if "=" in pair:
            key, value = pair.split("=", 1)
            parsed[key] = urllib.parse.unquote(value)
    return parsed


_DEFAULT_BOT_TOKEN = "8716981874:AAE2hzfIx8Gk0syIGwmp0ZzP36TRO9CtR8g"


async def get_telegram_bot_token(db: AsyncSession) -> str:
    """
    Get TELEGRAM_BOT_TOKEN from system_settings, fallback to .env, then default.
    """
    from ...modules.system_settings.service import SystemSettingService
    service = SystemSettingService(db)
    token = await service.get("TELEGRAM_BOT_TOKEN")
    if token and token.strip():
        return token.strip()
    if settings.TELEGRAM_BOT_TOKEN and settings.TELEGRAM_BOT_TOKEN.strip():
        return settings.TELEGRAM_BOT_TOKEN.strip()
    return _DEFAULT_BOT_TOKEN


def _verify_telegram_init_data_with_token(init_data: str, bot_token: str) -> bool:
    """Verify initData using given bot token (internal)."""
    if not bot_token:
        return False
    try:
        data = parse_init_data(init_data)
        received_hash = data.pop("hash", None)
        if not received_hash:
            return False
        data_check_string = "\n".join(
            f"{key}={value}" for key, value in sorted(data.items())
        )
        secret_key = hmac.new(
            "WebAppData".encode(),
            bot_token.encode(),
            hashlib.sha256
        ).digest()
        calculated_hash = hmac.new(
            secret_key,
            data_check_string.encode(),
            hashlib.sha256
        ).hexdigest()
        return hmac.compare_digest(calculated_hash, received_hash)
    except Exception:
        return False


def verify_telegram_init_data(init_data: str, bot_token: str) -> bool:
    """
    Verify Telegram WebApp initData signature.
    Caller must pass bot_token from get_telegram_bot_token(db).
    """
    return _verify_telegram_init_data_with_token(init_data, bot_token)


def extract_user_data(init_data: str) -> Optional[Dict]:
    """
    Extract user data from verified initData.
    
    Args:
        init_data: Raw initData string from Telegram WebApp
        
    Returns:
        Dictionary with user data or None if invalid
    """
    try:
        data = parse_init_data(init_data)
        
        # Extract user data from 'user' field (JSON string)
        user_str = data.get("user")
        if not user_str:
            return None
        
        import json
        user_data = json.loads(user_str)
        
        return {
            "id": user_data.get("id"),
            "first_name": user_data.get("first_name"),
            "last_name": user_data.get("last_name"),
            "username": user_data.get("username"),
            "photo_url": user_data.get("photo_url"),
            "auth_date": int(data.get("auth_date", 0)),
        }
    
    except Exception:
        return None
