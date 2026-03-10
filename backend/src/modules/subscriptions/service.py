"""Subscriptions module service."""
from sqlalchemy.ext.asyncio import AsyncSession
from typing import Optional, List
from uuid import UUID
from datetime import datetime, timedelta

from .repository import SubscriptionPlanRepository, SubscriptionRepository
from ..users.repository import UserRepository
from .schemas import SubscriptionPlanResponse, SubscriptionResponse, SubscriptionBase
from .models import Subscription, SubscriptionStatus
from ..telegram.bot_service import TelegramBotService
from ..channel_logs.service import ChannelAccessLogService
from ..channel_logs.models import ChannelAccessEventType


class SubscriptionService:
    """Service for subscription operations."""

    def __init__(self, db: AsyncSession):
        self.plan_repository = SubscriptionPlanRepository(db)
        self.subscription_repository = SubscriptionRepository(db)
        self.db = db
        self._bot_service: Optional[TelegramBotService] = None
        self.log_service = ChannelAccessLogService(db)

    async def _get_bot_service(self) -> TelegramBotService:
        """Get or create TelegramBotService (lazy, loads settings from DB)."""
        if self._bot_service is None:
            self._bot_service = await TelegramBotService.create(self.db)
        return self._bot_service

    async def get_plans(self) -> List[SubscriptionPlanResponse]:
        """Get all active subscription plans."""
        plans = await self.plan_repository.get_all_active()
        return [
            SubscriptionPlanResponse(
                id=str(p.id),
                name=p.name,
                description=p.description,
                price=float(p.price),
                first_month_price=float(p.first_month_price) if p.first_month_price else None,
                duration_days=p.duration_days,
                features=list(p.features) if p.features else [],
                is_active=p.is_active,
                created_at=p.created_at,
            )
            for p in plans
        ]

    async def get_user_subscription(
        self, user_id: str
    ) -> Optional[SubscriptionResponse]:
        """Get user's current subscription."""
        from uuid import UUID
        subscription = await self.subscription_repository.get_active_by_user_id(
            UUID(user_id)
        )
        if subscription:
            return SubscriptionResponse.model_validate(subscription)
        return None

    async def activate_subscription(self, subscription_id: UUID) -> Optional[Subscription]:
        """
        Activate subscription and grant channel access.
        
        Args:
            subscription_id: Subscription ID
            
        Returns:
            Updated subscription or None
        """
        subscription = await self.subscription_repository.get_by_id(subscription_id)
        if not subscription:
            return None

        # Check if already active
        if subscription.status == SubscriptionStatus.ACTIVE:
            return subscription

        # Update subscription status
        await self.subscription_repository.update(
            subscription_id,
            {"status": SubscriptionStatus.ACTIVE},
        )
        await self.db.refresh(subscription)

        # Grant channel access
        await self._grant_channel_access(subscription)

        return subscription

    async def _grant_channel_access(self, subscription) -> None:
        """
        Grant channel access to user.
        
        Args:
            subscription: Subscription object
        """
        # Load user relationship
        from sqlalchemy.orm import selectinload
        from sqlalchemy import select
        from .models import Subscription
        from datetime import datetime, timezone
        
        result = await self.db.execute(
            select(Subscription)
            .options(selectinload(Subscription.user))
            .where(Subscription.id == subscription.id)
        )
        subscription = result.scalar_one()
        
        if not subscription.user or not subscription.user.telegram_id:
            return

        # Check if user is already in channel
        bot_service = await self._get_bot_service()
        is_member = await bot_service.check_channel_membership(
            subscription.user.telegram_id
        )
        if is_member:
            # User already in channel, skip
            return

        # Check if existing invite link is still valid
        if subscription.telegram_invite_link and subscription.telegram_invite_link_expires:
            now = datetime.now(timezone.utc)
            if subscription.telegram_invite_link_expires > now:
                # Reuse existing invite link
                invite_link = subscription.telegram_invite_link
                message = (
                    "✅ Ваша подписка активирована!\n\n"
                    f"🔗 Ссылка для доступа к каналу:\n{invite_link}\n\n"
                    f"Ссылка действительна до {subscription.telegram_invite_link_expires.strftime('%d.%m.%Y %H:%M')}"
                )
                await bot_service.send_message(
                    subscription.user.telegram_id,
                    message,
                )
                return

        # Revoke old invite link if exists
        if subscription.telegram_invite_link:
            await bot_service.revoke_chat_invite_link(
                subscription.telegram_invite_link
            )

        # Create new invite link with member_limit=1 and expire_date=subscription_end
        invite_link = await bot_service.create_chat_invite_link(
            member_limit=1,
            expire_date=subscription.end_date,
        )

        if invite_link:
            # Store invite link in subscription
            await self.subscription_repository.update(
                subscription.id,
                {
                    "telegram_invite_link": invite_link,
                    "telegram_invite_link_expires": subscription.end_date,
                },
            )

            # Log invite creation
            await self.log_service.log_event(
                user_id=subscription.user.id,
                event_type=ChannelAccessEventType.INVITE_CREATED,
                telegram_id=subscription.user.telegram_id,
                subscription_id=subscription.id,
            )

            # Send message to user
            message = (
                "✅ Ваша подписка активирована!\n\n"
                f"🔗 Ссылка для доступа к каналу:\n{invite_link}\n\n"
                f"Ссылка действительна до {subscription.end_date.strftime('%d.%m.%Y %H:%M')}"
            )
            await bot_service.send_message(
                subscription.user.telegram_id,
                message,
            )

    async def create_subscription(
        self, user_id: str, subscription_data: SubscriptionBase
    ) -> SubscriptionResponse:
        """Create new subscription."""
        plan = await self.plan_repository.get_by_id(UUID(subscription_data.plan_id))
        if not plan:
            raise ValueError("Plan not found")

        start_date = datetime.utcnow()
        end_date = start_date + timedelta(days=plan.duration_days)

        subscription = await self.subscription_repository.create({
            "user_id": UUID(user_id),
            "plan_id": plan.id,
            "status": SubscriptionStatus.ACTIVE,
            "start_date": start_date,
            "end_date": end_date,
            "auto_renew": subscription_data.auto_renew,
        })

        await self._grant_channel_access(subscription)
        await self.db.refresh(subscription)
        return SubscriptionResponse.model_validate(subscription)

    async def cancel_subscription(
        self, user_id: str, subscription_id: str
    ) -> Optional[SubscriptionResponse]:
        """Cancel subscription."""
        if subscription_id:
            subscription = await self.subscription_repository.get_by_id(
                UUID(subscription_id)
            )
        else:
            subscription = await self.subscription_repository.get_active_by_user_id(
                UUID(user_id)
            )
        if not subscription:
            return None

        await self.subscription_repository.update(
            subscription.id,
            {
                "status": SubscriptionStatus.CANCELLED,
                "cancelled_at": datetime.utcnow(),
            },
        )
        await self.db.refresh(subscription)

        user_repo = UserRepository(self.db)
        user = await user_repo.get_by_id(subscription.user_id)
        if user and user.telegram_id:
            bot_service = await self._get_bot_service()
            await bot_service.remove_chat_member(user.telegram_id)
            try:
                await bot_service.close()
            except Exception:
                pass

        await self.db.refresh(subscription)
        return SubscriptionResponse.model_validate(subscription)
