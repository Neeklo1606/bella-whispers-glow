"""Telegram module service."""
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload
from sqlalchemy import select
from typing import Optional
from uuid import UUID
from datetime import datetime, timezone

from .repository import TelegramRepository
from .schemas import InviteLinkResponse, ChannelAccessRequest
from .bot_service import TelegramBotService
from ..subscriptions.repository import SubscriptionRepository
from ..subscriptions.models import Subscription
from ..users.repository import UserRepository


class TelegramService:
    """Service for Telegram operations."""

    def __init__(self, db: AsyncSession):
        self.db = db
        self.repository = TelegramRepository(db)

    async def generate_invite_link(
        self, user_id: str
    ) -> Optional[InviteLinkResponse]:
        """Generate invite link for user with active subscription."""
        subscription_repo = SubscriptionRepository(self.db)
        subscription = await subscription_repo.get_active_by_user_id(
            UUID(user_id)
        )
        if not subscription:
            return None

        result = await self.db.execute(
            select(Subscription)
            .options(selectinload(Subscription.user))
            .where(Subscription.id == subscription.id)
        )
        subscription = result.scalar_one()
        if not subscription.user or not subscription.user.telegram_id:
            return None

        if (
            subscription.telegram_invite_link
            and subscription.telegram_invite_link_expires
        ):
            now = datetime.now(timezone.utc)
            if subscription.telegram_invite_link_expires > now:
                expires_ts = int(
                    subscription.telegram_invite_link_expires.timestamp()
                )
                return InviteLinkResponse(
                    invite_link=subscription.telegram_invite_link,
                    expires_at=expires_ts,
                )

        bot_service = await TelegramBotService.create(self.db)
        invite_link = await bot_service.create_chat_invite_link(
            member_limit=1,
            expire_date=subscription.end_date,
        )
        try:
            await bot_service.close()
        except Exception:
            pass

        if not invite_link:
            return None

        await subscription_repo.update(
            subscription.id,
            {
                "telegram_invite_link": invite_link,
                "telegram_invite_link_expires": subscription.end_date,
            },
        )

        expires_ts = (
            int(subscription.end_date.timestamp())
            if subscription.end_date
            else None
        )
        return InviteLinkResponse(invite_link=invite_link, expires_at=expires_ts)

    async def add_user_to_channel(
        self, request: ChannelAccessRequest
    ) -> bool:
        """Add user to channel by creating invite link and sending it."""
        user_repo = UserRepository(self.db)
        user = await user_repo.get_by_id(UUID(request.user_id))
        if not user or not user.telegram_id:
            return False
        bot_service = await TelegramBotService.create(self.db)
        invite_link = await bot_service.create_chat_invite_link(
            member_limit=1,
        )
        if not invite_link:
            try:
                await bot_service.close()
            except Exception:
                pass
            return False
        result = await bot_service.send_message(
            user.telegram_id,
            f"🔗 Ссылка для доступа к каналу:\n{invite_link}",
        )
        try:
            await bot_service.close()
        except Exception:
            pass
        return result

    async def remove_user_from_channel(
        self, request: ChannelAccessRequest
    ) -> bool:
        """Remove user from Telegram channel."""
        user_repo = UserRepository(self.db)
        user = await user_repo.get_by_id(UUID(request.user_id))
        if not user or not user.telegram_id:
            return False
        bot_service = await TelegramBotService.create(self.db)
        result = await bot_service.remove_chat_member(user.telegram_id)
        try:
            await bot_service.close()
        except Exception:
            pass
        return result
