"""Users module service."""
from sqlalchemy.ext.asyncio import AsyncSession
from typing import Optional, List

from .repository import UserRepository
from .schemas import UserCreate, UserUpdate, UserResponse


class UserService:
    """Service for user operations."""

    def __init__(self, db: AsyncSession):
        self.repository = UserRepository(db)

    async def get_user(self, user_id: str) -> Optional[UserResponse]:
        """Get user by ID."""
        # TODO: Implement
        pass

    async def get_current_user(self, user_id: str) -> Optional[UserResponse]:
        """Get current user."""
        # TODO: Implement
        pass

    async def update_user(
        self, user_id: str, user_data: UserUpdate
    ) -> Optional[UserResponse]:
        """Update user."""
        # TODO: Implement
        pass

    async def get_all_users(
        self, skip: int = 0, limit: int = 100
    ) -> List[UserResponse]:
        """Get all users (admin)."""
        # TODO: Implement
        pass
