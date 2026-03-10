"""Broadcasts module repository."""
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from typing import Optional, List
from uuid import UUID

from .models import Broadcast


class BroadcastRepository:
    """Repository for broadcast operations."""

    def __init__(self, db: AsyncSession):
        self.db = db

    async def create(self, broadcast_data: dict) -> Broadcast:
        """Create new broadcast."""
        broadcast = Broadcast(**broadcast_data)
        self.db.add(broadcast)
        await self.db.flush()
        await self.db.refresh(broadcast)
        return broadcast

    async def get_by_id(self, broadcast_id: UUID) -> Optional[Broadcast]:
        """Get broadcast by ID."""
        result = await self.db.execute(
            select(Broadcast).where(Broadcast.id == broadcast_id)
        )
        return result.scalar_one_or_none()

    async def get_all(
        self, skip: int = 0, limit: int = 50
    ) -> List[Broadcast]:
        """Get all broadcasts with pagination."""
        result = await self.db.execute(
            select(Broadcast)
            .order_by(Broadcast.created_at.desc())
            .offset(skip)
            .limit(limit)
        )
        return list(result.scalars().all())

    async def update(
        self, broadcast_id: UUID, update_data: dict
    ) -> Optional[Broadcast]:
        """Update broadcast."""
        broadcast = await self.get_by_id(broadcast_id)
        if not broadcast:
            return None
        for key, value in update_data.items():
            if value is not None:
                setattr(broadcast, key, value)
        await self.db.flush()
        await self.db.refresh(broadcast)
        return broadcast

    async def update_status(
        self, broadcast_id: UUID, status: str
    ) -> Optional[Broadcast]:
        """Update broadcast status."""
        return await self.update(broadcast_id, {"status": status})
