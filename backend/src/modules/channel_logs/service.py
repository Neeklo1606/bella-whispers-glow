"""Channel access logs module service."""
from sqlalchemy.ext.asyncio import AsyncSession
from typing import Optional
from uuid import UUID

from .repository import ChannelAccessLogRepository
from .models import ChannelAccessEventType


class ChannelAccessLogService:
    """Service for channel access log operations."""

    def __init__(self, db: AsyncSession):
        self.repository = ChannelAccessLogRepository(db)

    async def log_event(
        self,
        user_id: UUID,
        event_type: ChannelAccessEventType,
        telegram_id: Optional[int] = None,
        subscription_id: Optional[UUID] = None,
    ) -> None:
        """
        Log channel access event.
        
        Args:
            user_id: User ID
            event_type: Event type
            telegram_id: Telegram user ID
            subscription_id: Subscription ID
        """
        await self.repository.create({
            "user_id": user_id,
            "telegram_id": telegram_id,
            "event_type": event_type,
            "subscription_id": subscription_id,
        })
