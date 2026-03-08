"""
Channel access logs module SQLAlchemy models.
"""
from sqlalchemy import Column, String, BigInteger, ForeignKey, Enum, Index
from sqlalchemy.orm import relationship
from sqlalchemy.dialects.postgresql import UUID
import enum

from ...core.db import BaseModel


class ChannelAccessEventType(str, enum.Enum):
    """Channel access event type enum."""

    JOIN = "JOIN"
    LEFT = "LEFT"
    KICKED = "KICKED"
    EXPIRED = "EXPIRED"
    INVITE_CREATED = "INVITE_CREATED"
    INVITE_REVOKED = "INVITE_REVOKED"


class ChannelAccessLog(BaseModel):
    """Channel access log model."""

    __tablename__ = "channel_access_logs"

    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=False, index=True)
    telegram_id = Column(BigInteger, nullable=True, index=True)
    event_type = Column(
        Enum(ChannelAccessEventType),
        nullable=False,
        index=True,
    )
    subscription_id = Column(
        UUID(as_uuid=True),
        ForeignKey("subscriptions.id"),
        nullable=True,
        index=True,
    )

    # Relationships
    user = relationship("User", back_populates="channel_access_logs")
    subscription = relationship("Subscription", back_populates="channel_access_logs")

    __table_args__ = (
        Index("idx_channel_access_logs_user_id", "user_id"),
        Index("idx_channel_access_logs_event_type", "event_type"),
        Index("idx_channel_access_logs_created_at", "created_at"),
    )
