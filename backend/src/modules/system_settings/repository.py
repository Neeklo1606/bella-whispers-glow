"""System settings module repository."""
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from typing import Optional, List
from uuid import UUID

from .models import SystemSetting


class SystemSettingRepository:
    """Repository for system setting operations."""

    def __init__(self, db: AsyncSession):
        self.db = db

    async def get_by_id(self, setting_id: UUID) -> Optional[SystemSetting]:
        """Get system setting by ID."""
        result = await self.db.execute(
            select(SystemSetting).where(SystemSetting.id == setting_id)
        )
        return result.scalar_one_or_none()

    async def get_by_key(self, key: str) -> Optional[SystemSetting]:
        """Get system setting by key."""
        result = await self.db.execute(
            select(SystemSetting).where(SystemSetting.key == key)
        )
        return result.scalar_one_or_none()

    async def get_all(self) -> List[SystemSetting]:
        """Get all system settings."""
        result = await self.db.execute(select(SystemSetting))
        return list(result.scalars().all())

    async def create(self, setting_data: dict) -> SystemSetting:
        """Create new system setting."""
        setting = SystemSetting(**setting_data)
        self.db.add(setting)
        await self.db.flush()
        await self.db.refresh(setting)
        return setting

    async def update(self, setting_id: UUID, data: dict) -> Optional[SystemSetting]:
        """Update system setting."""
        setting = await self.get_by_id(setting_id)
        if not setting:
            return None
        for key, value in data.items():
            if value is not None:
                setattr(setting, key, value)
        await self.db.flush()
        await self.db.refresh(setting)
        return setting

    async def update_by_key(self, key: str, data: dict) -> Optional[SystemSetting]:
        """Update system setting by key."""
        setting = await self.get_by_key(key)
        if not setting:
            return None
        for key_name, value in data.items():
            if value is not None:
                setattr(setting, key_name, value)
        await self.db.flush()
        await self.db.refresh(setting)
        return setting

    async def delete(self, setting_id: UUID) -> bool:
        """Delete system setting."""
        setting = await self.get_by_id(setting_id)
        if not setting:
            return False
        await self.db.delete(setting)
        await self.db.flush()
        return True

    async def delete_by_key(self, key: str) -> bool:
        """Delete system setting by key."""
        setting = await self.get_by_key(key)
        if not setting:
            return False
        await self.db.delete(setting)
        await self.db.flush()
        return True
