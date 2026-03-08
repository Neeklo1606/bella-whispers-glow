"""
Auth module service (business logic).
"""
from sqlalchemy.ext.asyncio import AsyncSession
from typing import Optional

from .schemas import TelegramAuthData, TokenResponse
from .strategies import TelegramAuthStrategy, AdminAuthStrategy
from ...core.security import verify_token, create_access_token


class AuthService:
    """Service for authentication operations."""

    def __init__(self, db: AsyncSession):
        """
        Initialize service.
        
        Args:
            db: Database session
        """
        self.db = db
        self.telegram_strategy = TelegramAuthStrategy()
        self.admin_strategy = AdminAuthStrategy()

    async def authenticate_telegram(
        self, auth_data: TelegramAuthData
    ) -> Optional[TokenResponse]:
        """
        Authenticate user via Telegram.
        
        Args:
            auth_data: Telegram authentication data
            
        Returns:
            Token response or None if authentication fails
        """
        return await self.telegram_strategy.authenticate(self.db, auth_data)

    async def login(self, email: str, password: str) -> Optional[TokenResponse]:
        """
        Login with email and password (Admin users).
        
        Args:
            email: User email
            password: User password
            
        Returns:
            Token response or None if login fails
        """
        return await self.admin_strategy.authenticate(self.db, email, password)

    async def refresh_token(self, refresh_token: str) -> Optional[TokenResponse]:
        """
        Refresh access token.
        
        Args:
            refresh_token: Refresh token
            
        Returns:
            New token response or None if refresh fails
        """
        payload = verify_token(refresh_token)
        if not payload:
            return None
        
        # Check if it's a refresh token
        if payload.get("type") != "refresh":
            return None
        
        user_id = payload.get("sub")
        role = payload.get("role")
        
        if not user_id:
            return None
        
        # Generate new tokens
        token_data = {"sub": user_id, "role": role}
        access_token = create_access_token(token_data)
        new_refresh_token = create_access_token(token_data)  # TODO: Use create_refresh_token
        
        return TokenResponse(
            access_token=access_token,
            refresh_token=new_refresh_token,
            token_type="bearer",
        )
