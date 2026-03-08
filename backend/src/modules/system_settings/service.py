"""System settings module service."""
import json
from sqlalchemy.ext.asyncio import AsyncSession
from typing import Optional, List, Dict

from .repository import SystemSettingRepository
from .models import SystemSetting
from .schemas import SettingResponse, SettingUpdate


class SystemSettingService:
    """Service for system setting operations."""

    def __init__(self, db: AsyncSession):
        self.repository = SystemSettingRepository(db)

    async def get(self, key: str) -> Optional[str]:
        """
        Get system setting value by key.
        
        Args:
            key: Setting key
            
        Returns:
            Setting value or None if not found
        """
        setting = await self.repository.get_by_key(key)
        if setting:
            return setting.value
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
        Supports value as str, int, bool, dict, list.
        """
        val = setting_data.value
        if val is None:
            value_str = ""
        elif isinstance(val, (dict, list)):
            value_str = json.dumps(val)
        else:
            value_str = str(val)
        existing = await self.repository.get_by_key(key)
        if existing:
            await self.repository.update_by_key(key, {"value": value_str})
            setting = await self.repository.get_by_key(key)
        else:
            setting = await self.repository.create(
                {"key": key, "value": value_str, "description": None}
            )
        return SettingResponse(
            key=setting.key,
            value=setting.value,
            description=setting.description,
        )
