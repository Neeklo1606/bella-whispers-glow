"""
Broadcasts module SQLAlchemy models.
"""
from sqlalchemy import (
    Column,
    String,
    ForeignKey,
    Text,
    DateTime,
    BigInteger,
    Enum,
    Index,
)
from sqlalchemy.orm import relationship
from sqlalchemy.dialects.postgresql import UUID
import enum

from ...core.db import BaseModel


class BroadcastStatus(str, enum.Enum):
    """Broadcast status enum."""

    DRAFT = "draft"
    SCHEDULED = "scheduled"
    SENT = "sent"
    FAILED = "failed"


class Broadcast(BaseModel):
    """Broadcast model."""

    __tablename__ = "broadcasts"

    created_by = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=False, index=True)
    title = Column(String(255), nullable=False)
    content = Column(Text, nullable=False)
    media_url = Column(String(512), nullable=True)
    scheduled_at = Column(DateTime(timezone=True), nullable=True, index=True)
    sent_at = Column(DateTime(timezone=True), nullable=True)
    status = Column(
        Enum(BroadcastStatus),
        default=BroadcastStatus.DRAFT,
        nullable=False,
        index=True,
    )
    telegram_message_id = Column(BigInteger, nullable=True)

    # Relationships
    creator = relationship("User", foreign_keys=[created_by])

    __table_args__ = (
        Index("idx_broadcasts_created_by", "created_by"),
        Index("idx_broadcasts_status", "status"),
        Index("idx_broadcasts_scheduled_at", "scheduled_at"),
        Index("idx_broadcasts_status_scheduled", "status", "scheduled_at"),
    )
