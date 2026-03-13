"""
Authentication strategies for different user types.
"""
from sqlalchemy.ext.asyncio import AsyncSession
from typing import Optional
from jose import JWTError

from ..users.models import User
from ..users.enums import UserRole
from ...core.security import verify_password, get_password_hash, create_access_token
from .schemas import TelegramAuthData, TokenResponse


class TelegramAuthStrategy:
    """Authentication strategy for Telegram users."""

    @staticmethod
    async def authenticate(
        db: AsyncSession, auth_data: TelegramAuthData
    ) -> Optional[TokenResponse]:
        """
        Authenticate Telegram user.
        
        Args:
            db: Database session
            auth_data: Telegram authentication data
            
        Returns:
            Token response or None if authentication fails
        """
        # TODO: Verify Telegram hash
        # For now, we'll trust the data from Mini App
        
        # Get or create user by telegram_id
        from ..users.repository import UserRepository
        repository = UserRepository(db)
        
        user = await repository.get_by_telegram_id(auth_data.id)
        
        if not user:
            # Create new Telegram user
            user = await repository.create({
                "telegram_id": auth_data.id,
                "username": auth_data.username,
                "first_name": auth_data.first_name,
                "last_name": auth_data.last_name,
                "avatar_url": auth_data.photo_url,
                "role": UserRole.USER,
            })
        
        # Generate tokens
        token_data = {"sub": str(user.id), "role": user.role.value}
        access_token = create_access_token(token_data)
        refresh_token = create_access_token(token_data)  # TODO: Use create_refresh_token
        
        return TokenResponse(
            access_token=access_token,
            refresh_token=refresh_token,
            token_type="bearer",
        )


class AdminAuthStrategy:
    """Authentication strategy for Admin users."""

    @staticmethod
    async def authenticate(
        db: AsyncSession, email: str, password: str
    ) -> Optional[TokenResponse]:
        """
        Authenticate admin user with email and password.
        
        Args:
            db: Database session
            email: User email
            password: Plain text password
            
        Returns:
            Token response or None if authentication fails
        """
        from ..users.repository import UserRepository
        repository = UserRepository(db)
        
        # Get user by email
        user = await repository.get_by_email(email)
        
        if not user:
            return None
        
        # Check if user has password (admin user)
        if not user.password_hash:
            return None
        
        # Verify password
        if not verify_password(password, user.password_hash):
            return None
        
        # Check if user has admin role
        if user.role not in (UserRole.ADMIN, UserRole.SUPER_ADMIN):
            return None
        
        # Generate tokens
        token_data = {"sub": str(user.id), "role": user.role.value}
        access_token = create_access_token(token_data)
        refresh_token = create_access_token(token_data)  # TODO: Use create_refresh_token
        
        return TokenResponse(
            access_token=access_token,
            refresh_token=refresh_token,
            token_type="bearer",
        )
