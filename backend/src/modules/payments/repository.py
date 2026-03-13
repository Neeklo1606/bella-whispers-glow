"""Payments module repository."""
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from typing import Optional, List
from uuid import UUID

from .models import Payment, PaymentStatus


class PaymentRepository:
    """Repository for payment operations."""

    def __init__(self, db: AsyncSession):
        self.db = db

    async def create(self, payment_data: dict) -> Payment:
        """Create new payment. Maps metadata to provider_metadata for model compatibility."""
        data = dict(payment_data)
        if "metadata" in data:
            data["provider_metadata"] = data.pop("metadata")
        payment = Payment(**data)
        self.db.add(payment)
        await self.db.flush()
        await self.db.refresh(payment)
        return payment

    async def get_by_id(self, payment_id: UUID) -> Optional[Payment]:
        """Get payment by ID."""
        result = await self.db.execute(
            select(Payment).where(Payment.id == payment_id)
        )
        return result.scalar_one_or_none()

    async def get_by_provider_payment_id(
        self, provider_payment_id: str
    ) -> Optional[Payment]:
        """Get payment by provider payment ID."""
        result = await self.db.execute(
            select(Payment).where(Payment.provider_payment_id == provider_payment_id)
        )
        return result.scalar_one_or_none()

    async def update(self, payment_id: UUID, data: dict) -> Optional[Payment]:
        """Update payment."""
        payment = await self.get_by_id(payment_id)
        if not payment:
            return None

        for key, value in data.items():
            if value is not None:
                setattr(payment, key, value)

        await self.db.flush()
        await self.db.refresh(payment)
        return payment

    async def get_by_user_id(
        self, user_id: UUID, skip: int = 0, limit: int = 100
    ) -> List[Payment]:
        """Get payments for user."""
        result = await self.db.execute(
            select(Payment)
            .where(Payment.user_id == user_id)
            .order_by(Payment.created_at.desc())
            .offset(skip)
            .limit(limit)
        )
        return list(result.scalars().all())

    async def get_pending_payments(self) -> List[Payment]:
        """Get all pending payments."""
        result = await self.db.execute(
            select(Payment).where(Payment.status == PaymentStatus.PENDING)
        )
        return list(result.scalars().all())

    async def get_pending_with_provider_id(self) -> List[Payment]:
        """Get pending payments that have provider_payment_id (can be synced from YooKassa)."""
        result = await self.db.execute(
            select(Payment).where(
                Payment.status == PaymentStatus.PENDING,
                Payment.provider_payment_id.isnot(None),
                Payment.provider_payment_id != "",
            )
        )
        return list(result.scalars().all())

    async def get_completed_without_subscription(self) -> List[Payment]:
        """Get completed payments that have plan_id but no subscription_id (need backfill)."""
        result = await self.db.execute(
            select(Payment).where(
                Payment.status == PaymentStatus.COMPLETED,
                Payment.plan_id.isnot(None),
                Payment.subscription_id.is_(None),
            )
        )
        return list(result.scalars().all())
