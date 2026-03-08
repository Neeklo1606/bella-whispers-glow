"""
Payments module SQLAlchemy models.
"""
from sqlalchemy import (
    Column,
    String,
    ForeignKey,
    Numeric,
    DateTime,
    JSON,
    Enum,
    Index,
)
from sqlalchemy.orm import relationship
from sqlalchemy.dialects.postgresql import UUID
import enum

from ...core.db import BaseModel


class PaymentStatus(str, enum.Enum):
    """Payment status enum."""

    PENDING = "pending"
    COMPLETED = "completed"
    FAILED = "failed"
    REFUNDED = "refunded"


class Payment(BaseModel):
    """Payment model."""

    __tablename__ = "payments"

    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=False, index=True)
    plan_id = Column(
        UUID(as_uuid=True),
        ForeignKey("subscription_plans.id"),
        nullable=True,
        index=True,
    )
    subscription_id = Column(
        UUID(as_uuid=True),
        ForeignKey("subscriptions.id"),
        nullable=True,
        index=True,
    )
    amount = Column(Numeric(10, 2), nullable=False)
    currency = Column(String(3), default="RUB", nullable=False)
    status = Column(
        Enum(PaymentStatus, values_callable=lambda obj: [e.value for e in obj]),
        default=PaymentStatus.PENDING,
        nullable=False,
        index=True,
    )
    provider = Column(String(50), nullable=False)  # Renamed from payment_provider
    provider_payment_id = Column(String(255), nullable=True, unique=True, index=True)
    payment_url = Column(String(512), nullable=True)
    paid_at = Column(DateTime(timezone=True), nullable=True)
    provider_metadata = Column("metadata", JSON, nullable=True)  # DB column 'metadata', attr renamed (reserved in SQLAlchemy)

    # Relationships
    user = relationship("User", back_populates="payments")
    subscription = relationship(
        "Subscription",
        back_populates="payments",
        foreign_keys=[subscription_id],
    )

    __table_args__ = (
        Index("idx_payments_user_id", "user_id"),
        Index("idx_payments_status", "status"),
        Index("idx_payments_provider_payment_id", "provider_payment_id"),
        Index("idx_payments_user_status", "user_id", "status"),
    )
