"""Users module repository."""
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from typing import Optional, List
from uuid import UUID

from .models import User
from .enums import UserRole
from ...core.security import get_password_hash


class UserRepository:
    """Repository for user operations."""

    def __init__(self, db: AsyncSession):
        self.db = db

    async def get_by_id(self, user_id: UUID) -> Optional[User]:
        """Get user by ID."""
        result = await self.db.execute(select(User).where(User.id == user_id))
        return result.scalar_one_or_none()

    async def get_by_telegram_id(self, telegram_id: int) -> Optional[User]:
        """Get user by Telegram ID."""
        result = await self.db.execute(
            select(User).where(User.telegram_id == telegram_id)
        )
        return result.scalar_one_or_none()

    async def get_by_email(self, email: str) -> Optional[User]:
        """Get user by email."""
        result = await self.db.execute(select(User).where(User.email == email))
        return result.scalar_one_or_none()

    async def create(self, user_data: dict) -> User:
        """Create new user."""
        # Hash password if provided
        if "password" in user_data and user_data["password"]:
            user_data["password_hash"] = get_password_hash(user_data.pop("password"))
        
        user = User(**user_data)
        self.db.add(user)
        await self.db.flush()
        await self.db.refresh(user)
        return user

    async def update(self, user_id: UUID, user_data: dict) -> Optional[User]:
        """Update user."""
        user = await self.get_by_id(user_id)
        if not user:
            return None
        
        # Hash password if provided
        if "password" in user_data and user_data["password"]:
            user_data["password_hash"] = get_password_hash(user_data.pop("password"))
        
        for key, value in user_data.items():
            if value is not None:
                setattr(user, key, value)
        
        await self.db.flush()
        await self.db.refresh(user)
        return user

    async def get_all(self, skip: int = 0, limit: int = 100) -> List[User]:
        """Get all users with pagination."""
        result = await self.db.execute(
            select(User).offset(skip).limit(limit)
        )
        return list(result.scalars().all())

    async def get_by_ids(self, user_ids: List[UUID]) -> List[User]:
        """Get users by IDs, only those with telegram_id."""
        if not user_ids:
            return []
        result = await self.db.execute(
            select(User).where(
                User.id.in_(user_ids),
                User.telegram_id.isnot(None),
            )
        )
        return list(result.scalars().all())

    async def get_all_with_telegram(self, limit: int = 10000) -> List[User]:
        """Get all users that have telegram_id (for broadcasts)."""
        result = await self.db.execute(
            select(User).where(User.telegram_id.isnot(None)).limit(limit)
        )
        return list(result.scalars().all())

    async def delete(self, user_id: UUID) -> bool:
        """Delete user by ID."""
        user = await self.get_by_id(user_id)
        if not user:
            return False
        await self.db.delete(user)
        await self.db.flush()
        return True
