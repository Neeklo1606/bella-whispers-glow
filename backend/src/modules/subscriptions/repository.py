"""Subscriptions module repository."""
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, and_
from typing import Optional, List
from uuid import UUID
from datetime import datetime

from .models import Subscription, SubscriptionPlan, SubscriptionStatus


class SubscriptionPlanRepository:
    """Repository for subscription plan operations."""

    def __init__(self, db: AsyncSession):
        self.db = db

    async def get_by_id(self, plan_id: UUID) -> Optional[SubscriptionPlan]:
        """Get subscription plan by ID."""
        result = await self.db.execute(
            select(SubscriptionPlan).where(SubscriptionPlan.id == plan_id)
        )
        return result.scalar_one_or_none()

    async def get_all(self) -> List[SubscriptionPlan]:
        """Get all subscription plans."""
        result = await self.db.execute(select(SubscriptionPlan))
        return list(result.scalars().all())

    async def get_all_active(self) -> List[SubscriptionPlan]:
        """Get all active subscription plans."""
        result = await self.db.execute(
            select(SubscriptionPlan).where(SubscriptionPlan.is_active == True)
        )
        return list(result.scalars().all())

    async def create(self, plan_data: dict) -> SubscriptionPlan:
        """Create new subscription plan."""
        plan = SubscriptionPlan(**plan_data)
        self.db.add(plan)
        await self.db.flush()
        await self.db.refresh(plan)
        return plan

    async def update(
        self, plan_id: UUID, update_data: dict
    ) -> Optional[SubscriptionPlan]:
        """Update subscription plan."""
        plan = await self.get_by_id(plan_id)
        if not plan:
            return None
        for key, value in update_data.items():
            if value is not None:
                setattr(plan, key, value)
        await self.db.flush()
        await self.db.refresh(plan)
        return plan

    async def delete(self, plan_id: UUID) -> bool:
        """Delete subscription plan."""
        plan = await self.get_by_id(plan_id)
        if not plan:
            return False
        await self.db.delete(plan)
        await self.db.flush()
        return True


class SubscriptionRepository:
    """Repository for subscription operations."""

    def __init__(self, db: AsyncSession):
        self.db = db

    async def get_by_id(self, subscription_id: UUID) -> Optional[Subscription]:
        """Get subscription by ID."""
        result = await self.db.execute(
            select(Subscription).where(Subscription.id == subscription_id)
        )
        return result.scalar_one_or_none()

    async def get_active_by_user_id(self, user_id: UUID) -> Optional[Subscription]:
        """Get active subscription for user."""
        result = await self.db.execute(
            select(Subscription).where(
                and_(
                    Subscription.user_id == user_id,
                    Subscription.status == SubscriptionStatus.ACTIVE,
                )
            )
        )
        return result.scalar_one_or_none()

    async def get_all_by_user_id(self, user_id: UUID, limit: int = 50) -> List[Subscription]:
        """Get all subscriptions for user."""
        result = await self.db.execute(
            select(Subscription)
            .where(Subscription.user_id == user_id)
            .order_by(Subscription.created_at.desc())
            .limit(limit)
        )
        return list(result.scalars().all())

    async def get_expired_subscriptions(self) -> List[Subscription]:
        """Get subscriptions that have expired but are still marked as active."""
        now = datetime.utcnow()
        result = await self.db.execute(
            select(Subscription).where(
                and_(
                    Subscription.status == SubscriptionStatus.ACTIVE,
                    Subscription.end_date < now,
                )
            )
        )
        return list(result.scalars().all())

    async def create(self, subscription_data: dict) -> Subscription:
        """Create new subscription."""
        subscription = Subscription(**subscription_data)
        self.db.add(subscription)
        await self.db.flush()
        await self.db.refresh(subscription)
        return subscription

    async def update(self, subscription_id: UUID, data: dict) -> Optional[Subscription]:
        """Update subscription."""
        subscription = await self.get_by_id(subscription_id)
        if not subscription:
            return None

        for key, value in data.items():
            if value is not None:
                setattr(subscription, key, value)

        await self.db.flush()
        await self.db.refresh(subscription)
        return subscription

    async def delete(self, subscription_id: UUID) -> bool:
        """Delete subscription."""
        subscription = await self.get_by_id(subscription_id)
        if not subscription:
            return False
        await self.db.delete(subscription)
        await self.db.flush()
        return True
