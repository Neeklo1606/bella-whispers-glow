"""System settings module service."""
import time
from sqlalchemy.ext.asyncio import AsyncSession
from typing import Optional, List, Dict, Tuple

from .repository import SystemSettingRepository
from .models import SystemSetting
from .schemas import SettingResponse, SettingUpdate

# Simple in-memory cache: key -> (value, expiry_timestamp)
# TTL 60 seconds
_SETTINGS_CACHE: Dict[str, Tuple[str, float]] = {}
_CACHE_TTL_SECONDS = 60


def _cache_get(key: str) -> Optional[str]:
    """Get from cache if not expired."""
    entry = _SETTINGS_CACHE.get(key)
    if not entry:
        return None
    value, expiry = entry
    if time.monotonic() > expiry:
        del _SETTINGS_CACHE[key]
        return None
    return value


def _cache_set(key: str, value: str) -> None:
    """Store in cache with TTL."""
    _SETTINGS_CACHE[key] = (value, time.monotonic() + _CACHE_TTL_SECONDS)


def _cache_invalidate(key: str) -> None:
    """Invalidate cache for key (on update/delete)."""
    _SETTINGS_CACHE.pop(key, None)


class SystemSettingService:
    """Service for system setting operations."""

    def __init__(self, db: AsyncSession):
        self.repository = SystemSettingRepository(db)

    async def get(self, key: str) -> Optional[str]:
        """
        Get system setting value by key. Cached 60 seconds.
        
        Args:
            key: Setting key
            
        Returns:
            Setting value or None if not found
        """
        cached = _cache_get(key)
        if cached is not None:
            return cached
        setting = await self.repository.get_by_key(key)
        if setting:
            val = setting.value or ""
            _cache_set(key, val)
            return val
        return None

    async def set(self, key: str, value: str, description: Optional[str] = None) -> SystemSetting:
        """
        Set system setting value by key.
        Creates setting if it doesn't exist, updates if it does.
        
        Args:
            key: Setting key
            value: Setting value
            description: Optional description
            
        Returns:
            SystemSetting instance
        """
        existing = await self.repository.get_by_key(key)
        
        if existing:
            # Update existing setting
            update_data = {"value": value}
            if description is not None:
                update_data["description"] = description
            return await self.repository.update_by_key(key, update_data)
        else:
            # Create new setting
            return await self.repository.create({
                "key": key,
                "value": value,
                "description": description,
            })

    async def get_all(self) -> List[Dict[str, str]]:
        """
        Get all system settings.
        
        Returns:
            List of dictionaries with key, value, and description
        """
        settings = await self.repository.get_all()
        return [
            {
                "key": setting.key,
                "value": setting.value,
                "description": setting.description,
            }
            for setting in settings
        ]

    async def get_setting_object(self, key: str) -> Optional[SystemSetting]:
        """
        Get system setting object by key.
        
        Args:
            key: Setting key
            
        Returns:
            SystemSetting instance or None
        """
        return await self.repository.get_by_key(key)

    async def delete(self, key: str) -> bool:
        """
        Delete system setting by key.
        
        Args:
            key: Setting key
            
        Returns:
            True if deleted, False if not found
        """
        _cache_invalidate(key)
        return await self.repository.delete_by_key(key)

    async def get_settings(self) -> Dict[str, SettingResponse]:
        """Get all settings as dict of SettingResponse."""
        settings = await self.repository.get_all()
        return {
            s.key: SettingResponse(
                key=s.key,
                value=s.value,
                description=s.description,
            )
            for s in settings
        }

    async def get_setting(self, key: str) -> Optional[SettingResponse]:
        """Get setting by key as SettingResponse."""
        setting = await self.repository.get_by_key(key)
        if not setting:
            return None
        return SettingResponse(
            key=setting.key,
            value=setting.value,
            description=setting.description,
        )

    async def update_setting(self, key: str, setting_data: SettingUpdate) -> SettingResponse:
        """
        Update setting by key. Creates if not exists.
        Supports value as str, int, bool, dict, list. Passed to JSON column as-is.
        """
        val = setting_data.value
        if val is None:
            val = ""
        existing = await self.repository.get_by_key(key)
        _cache_invalidate(key)
        if existing:
            await self.repository.update_by_key(key, {"value": val})
            setting = await self.repository.get_by_key(key)
        else:
            setting = await self.repository.create(
                {"key": key, "value": val, "description": None}
            )
        return SettingResponse(
            key=setting.key,
            value=setting.value,
            description=setting.description,
        )
