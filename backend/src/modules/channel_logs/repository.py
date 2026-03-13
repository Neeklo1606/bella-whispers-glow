"""Channel access logs module repository."""
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from typing import Optional, List
from uuid import UUID

from .models import ChannelAccessLog, ChannelAccessEventType


class ChannelAccessLogRepository:
    """Repository for channel access log operations."""

    def __init__(self, db: AsyncSession):
        self.db = db

    async def create(self, log_data: dict) -> ChannelAccessLog:
        """Create new channel access log."""
        log = ChannelAccessLog(**log_data)
        self.db.add(log)
        await self.db.flush()
        await self.db.refresh(log)
        return log

    async def get_by_user_id(self, user_id: UUID, limit: int = 100) -> List[ChannelAccessLog]:
        """Get logs for user."""
        result = await self.db.execute(
            select(ChannelAccessLog)
            .where(ChannelAccessLog.user_id == user_id)
            .order_by(ChannelAccessLog.created_at.desc())
            .limit(limit)
        )
        return list(result.scalars().all())

    async def get_by_subscription_id(
        self, subscription_id: UUID
    ) -> List[ChannelAccessLog]:
        """Get logs for subscription."""
        result = await self.db.execute(
            select(ChannelAccessLog)
            .where(ChannelAccessLog.subscription_id == subscription_id)
            .order_by(ChannelAccessLog.created_at.desc())
        )
        return list(result.scalars().all())
