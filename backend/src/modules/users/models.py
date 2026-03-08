"""
Users module SQLAlchemy models.
"""
from sqlalchemy import Column, String, BigInteger, Enum, Index
from sqlalchemy.orm import relationship

from ...core.db import BaseModel
from .enums import UserRole

# Export enum for use in other modules
__all__ = ["User", "UserRole"]


class User(BaseModel):
    """User model."""

    __tablename__ = "users"

    telegram_id = Column(BigInteger, unique=True, nullable=True, index=True)
    username = Column(String(255), nullable=True)
    first_name = Column(String(255), nullable=True)
    last_name = Column(String(255), nullable=True)
    avatar_url = Column(String(512), nullable=True)
    
    email = Column(String(255), nullable=True, unique=True, index=True)
    password_hash = Column(String(255), nullable=True)
    
    role = Column(
        Enum(UserRole, values_callable=lambda obj: [e.value for e in obj]),
        default=UserRole.USER,
        nullable=False,
        index=True,
    )

    # Relationships
    subscriptions = relationship(
        "Subscription",
        back_populates="user",
        cascade="all, delete-orphan",
    )
    payments = relationship(
        "Payment",
        back_populates="user",
        cascade="all, delete-orphan",
    )
    channel_access_logs = relationship(
        "ChannelAccessLog",
        back_populates="user",
        cascade="all, delete-orphan",
    )

    __table_args__ = (
        Index("idx_users_telegram_id", "telegram_id"),
        Index("idx_users_email", "email"),
        Index("idx_users_role", "role"),
    )

    @property
    def is_admin(self) -> bool:
        """Check if user is admin or super_admin."""
        return self.role in (UserRole.ADMIN, UserRole.SUPER_ADMIN)

    @property
    def is_telegram_user(self) -> bool:
        """Check if user is Telegram user."""
        return self.telegram_id is not None

    @property
    def is_admin_user(self) -> bool:
        """Check if user is admin user (email/password)."""
        return self.email is not None and self.password_hash is not None
