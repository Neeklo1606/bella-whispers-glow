"""
Bot runtime settings from backend GET /api/settings.
Refreshes every 5 minutes.
"""
import asyncio
import logging
import time
from typing import Optional

import httpx

from .config import get_bot_config

logger = logging.getLogger(__name__)

_REFRESH_INTERVAL = 300  # 5 minutes
_cache: dict[str, str] = {}
_cache_lock = asyncio.Lock()
_last_fetch: float = 0
_refresh_task: Optional[asyncio.Task] = None

_DEFAULTS = {
    "MINIAPP_URL": "https://app.bellahasias.ru",
    "OFFER_URL": "https://bellahasias.ru/privacy",
    "SUPPORT_USERNAME": "Bella_hasias",
    "CONTACT_LINK": "https://t.me/Bella_hasias",
}


def _parse_value(val: object) -> str:
    """Extract string from setting value (may be dict with 'value' key or direct)."""
    if val is None:
        return ""
    if isinstance(val, str):
        return val.strip()
    if isinstance(val, dict) and "value" in val:
        v = val["value"]
        return str(v).strip() if v is not None else ""
    return str(val).strip()


async def _fetch_settings() -> None:
    """Fetch settings from GET /api/settings."""
    global _cache, _last_fetch
    config = get_bot_config()
    url = f"{config.API_BASE_URL.rstrip('/')}/api/settings"
    try:
        async with httpx.AsyncClient(timeout=10.0) as client:
            r = await client.get(url)
            if r.status_code == 200:
                data = r.json()
                new_cache: dict[str, str] = {}
                keys = (
                    "MINIAPP_URL", "OFFER_URL", "SUPPORT_USERNAME", "CONTACT_LINK",
                    "MSG_TARIFFS_INTRO", "MSG_TARIFFS_ACTIVE", "MSG_SUBSCRIPTION_ACTIVE",
                    "MSG_SUBSCRIPTION_NONE", "MSG_SUBSCRIPTION_EXPIRED_OFFER",
                )
                for key in keys:
                    if key in data:
                        entry = data[key]
                        if isinstance(entry, dict):
                            val = _parse_value(entry.get("value", ""))
                        else:
                            val = _parse_value(entry)
                        if val:
                            new_cache[key] = val
                async with _cache_lock:
                    _cache.clear()
                    _cache.update(new_cache)
                    _last_fetch = time.monotonic()
    except Exception as e:
        logger.warning("Failed to fetch runtime settings: %s", e)


def get(key: str) -> str:
    """Get cached setting, or default. Sync, uses current cache."""
    return _cache.get(key, _DEFAULTS.get(key, ""))


async def get_async(key: str) -> str:
    """Get setting; trigger fetch if cache empty or stale."""
    now = time.monotonic()
    need_fetch = False
    async with _cache_lock:
        if not _cache or (now - _last_fetch) > _REFRESH_INTERVAL:
            need_fetch = True
    if need_fetch:
        await _fetch_settings()
    return get(key)


def start_refresh_loop() -> asyncio.Task:
    """Start background refresh task (every 5 min)."""
    global _refresh_task

    async def _loop() -> None:
        await _fetch_settings()
        while True:
            await asyncio.sleep(_REFRESH_INTERVAL)
            await _fetch_settings()

    _refresh_task = asyncio.create_task(_loop())
    return _refresh_task
