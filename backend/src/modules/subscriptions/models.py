"""
Subscriptions module SQLAlchemy models.
"""
from sqlalchemy import (
    Column,
    String,
    ForeignKey,
    Integer,
    Numeric,
    Boolean,
    DateTime,
    JSON,
    Enum,
    Index,
)
from sqlalchemy.orm import relationship
from sqlalchemy.dialects.postgresql import UUID
import enum

from ...core.db import BaseModel


class SubscriptionStatus(str, enum.Enum):
    """Subscription status enum."""

    ACTIVE = "active"
    EXPIRED = "expired"
    CANCELLED = "cancelled"
    PENDING = "pending"


class SubscriptionPlan(BaseModel):
    """Subscription plan model."""

    __tablename__ = "subscription_plans"

    name = Column(String(255), nullable=False)
    description = Column(String(1000), nullable=True)
    price = Column(Numeric(10, 2), nullable=False)
    first_month_price = Column(Numeric(10, 2), nullable=True)
    duration_days = Column(Integer, default=30, nullable=False)
    features = Column(JSON, nullable=True, default=list)
    is_active = Column(Boolean, default=True, nullable=False)
    
    # Additional fields for plans module
    currency = Column(String(3), default="RUB", nullable=False)
    telegram_channel_id = Column(String(50), nullable=True)

    # Relationships
    subscriptions = relationship(
        "Subscription",
        back_populates="plan",
        cascade="all, delete-orphan",
    )

    __table_args__ = (
        Index("idx_subscription_plans_is_active", "is_active"),
    )


class Subscription(BaseModel):
    """Subscription model."""

    __tablename__ = "subscriptions"

    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=False, index=True)
    plan_id = Column(UUID(as_uuid=True), ForeignKey("subscription_plans.id"), nullable=False)
    payment_id = Column(
        UUID(as_uuid=True),
        ForeignKey("payments.id"),
        nullable=True,
        index=True,
    )
    status = Column(
        Enum(SubscriptionStatus),
        default=SubscriptionStatus.PENDING,
        nullable=False,
        index=True,
    )
    start_date = Column(DateTime(timezone=True), nullable=True)
    end_date = Column(DateTime(timezone=True), nullable=True, index=True)
    auto_renew = Column(Boolean, default=True, nullable=False)
    cancelled_at = Column(DateTime(timezone=True), nullable=True)
    next_billing_date = Column(DateTime(timezone=True), nullable=True)
    
    # Telegram channel invite link
    telegram_invite_link = Column(String(512), nullable=True)
    telegram_invite_link_expires = Column(DateTime(timezone=True), nullable=True)

    # Relationships
    user = relationship("User", back_populates="subscriptions")
    plan = relationship("SubscriptionPlan", back_populates="subscriptions")
    payment = relationship("Payment", foreign_keys=[payment_id], post_update=True)
    payments = relationship(
        "Payment",
        back_populates="subscription",
        cascade="all, delete-orphan",
    )
    channel_access_logs = relationship(
        "ChannelAccessLog",
        back_populates="subscription",
        cascade="all, delete-orphan",
    )

    __table_args__ = (
        Index("idx_subscriptions_user_id", "user_id"),
        Index("idx_subscriptions_status", "status"),
        Index("idx_subscriptions_end_date", "end_date"),
        Index("idx_subscriptions_user_status", "user_id", "status"),
    )
