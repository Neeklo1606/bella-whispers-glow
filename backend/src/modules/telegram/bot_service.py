"""
Telegram Bot service for channel operations.
Uses a cached bot instance for performance; recreates only when token changes.
"""
import asyncio
import logging
from datetime import datetime
from typing import Optional

from sqlalchemy.ext.asyncio import AsyncSession
from aiogram import Bot
from aiogram.exceptions import TelegramAPIError

from ...core.config import settings
from ..system_settings.service import SystemSettingService

logger = logging.getLogger(__name__)

# Setting keys for database lookup
TELEGRAM_BOT_TOKEN_KEY = "TELEGRAM_BOT_TOKEN"
TELEGRAM_CHANNEL_ID_KEY = "TELEGRAM_CHANNEL_ID"

# Module-level cache: bot instance is reused until token changes
_cached_token: Optional[str] = None
_cached_channel_id: Optional[str] = None
_cached_bot: Optional[Bot] = None
_cache_lock = asyncio.Lock()


class TelegramBotService:
    """Service for Telegram Bot API operations."""

    def __init__(self, token: str, channel_id: str, bot: Optional[Bot] = None):
        """Initialize bot service with token, channel_id, and optionally a shared bot instance."""
        self.channel_id = channel_id
        self._is_shared = bot is not None
        self.bot = bot if bot is not None else Bot(token=token)

    @classmethod
    async def create(cls, db: AsyncSession) -> "TelegramBotService":
        """
        Create TelegramBotService with settings loaded from database.
        Falls back to ENV if setting not found in DB.
        Returns a cached instance when token is unchanged.
        """
        global _cached_token, _cached_channel_id, _cached_bot

        setting_service = SystemSettingService(db)
        token = await setting_service.get(TELEGRAM_BOT_TOKEN_KEY)
        channel_id = await setting_service.get(TELEGRAM_CHANNEL_ID_KEY)

        if not token:
            token = settings.TELEGRAM_BOT_TOKEN
        if not channel_id:
            channel_id = settings.TELEGRAM_CHANNEL_ID

        async with _cache_lock:
            if _cached_token == token and _cached_bot is not None:
                return cls(token=token, channel_id=channel_id, bot=_cached_bot)

            if _cached_bot is not None:
                try:
                    await _cached_bot.session.close()
                except Exception as e:
                    logger.warning(f"Error closing previous bot session: {e}")

            _cached_bot = Bot(token=token)
            _cached_token = token
            _cached_channel_id = channel_id
            return cls(token=token, channel_id=channel_id, bot=_cached_bot)

    async def revoke_chat_invite_link(self, invite_link: str) -> bool:
        """
        Revoke invite link for Telegram channel.
        
        Args:
            invite_link: Invite link URL to revoke
            
        Returns:
            True if successful, False otherwise
        """
        try:
            await self.bot.revoke_chat_invite_link(
                chat_id=self.channel_id,
                invite_link=invite_link,
            )
            return True
        except TelegramAPIError as e:
            # Link might already be revoked or invalid
            logger.warning(f"Failed to revoke invite link (might already be revoked): {e}")
            return False
        except Exception as e:
            logger.error(f"Unexpected error revoking invite link: {e}")
            return False

    async def create_chat_invite_link(
        self,
        member_limit: int = 1,
        expire_date: Optional[datetime] = None,
    ) -> Optional[str]:
        """
        Create invite link for Telegram channel.
        
        Args:
            member_limit: Maximum number of members that can join using this link (default: 1)
            expire_date: Expiration date for the invite link
            
        Returns:
            Invite link URL or None if failed
        """
        try:
            result = await self.bot.create_chat_invite_link(
                chat_id=self.channel_id,
                member_limit=member_limit,
                expire_date=expire_date,
            )
            return result.invite_link
        except TelegramAPIError as e:
            logger.error(f"Failed to create invite link: {e}")
            return None
        except Exception as e:
            logger.error(f"Unexpected error creating invite link: {e}")
            return None

    async def check_channel_membership(self, user_id: int) -> bool:
        """
        Check if user is already a member of the channel.
        
        Args:
            user_id: Telegram user ID
            
        Returns:
            True if user is a member, False otherwise
        """
        try:
            member = await self.bot.get_chat_member(
                chat_id=self.channel_id,
                user_id=user_id,
            )
            # Check if user is a member (not left/kicked/banned)
            return member.status in ["member", "administrator", "creator"]
        except TelegramAPIError as e:
            # If user is not found or not a member, API returns error
            if "user not found" in str(e).lower() or "member not found" in str(e).lower():
                return False
            logger.error(f"Failed to check channel membership: {e}")
            return False
        except Exception as e:
            logger.error(f"Unexpected error checking membership: {e}")
            return False

    async def remove_chat_member(self, user_id: int) -> bool:
        """
        Remove user from Telegram channel using ban/unban.
        
        Args:
            user_id: Telegram user ID
            
        Returns:
            True if successful, False otherwise
        """
        try:
            # Ban user
            await self.bot.ban_chat_member(
                chat_id=self.channel_id,
                user_id=user_id,
            )
            # Unban immediately to allow re-joining later
            await self.bot.unban_chat_member(
                chat_id=self.channel_id,
                user_id=user_id,
                only_if_banned=True,
            )
            return True
        except TelegramAPIError as e:
            logger.error(f"Failed to remove user from channel: {e}")
            return False
        except Exception as e:
            logger.error(f"Unexpected error removing user: {e}")
            return False

    async def send_message(self, user_id: int, text: str) -> bool:
        """
        Send message to user via bot.
        
        Args:
            user_id: Telegram user ID
            text: Message text
            
        Returns:
            True if successful, False otherwise
        """
        try:
            await self.bot.send_message(
                chat_id=user_id,
                text=text,
            )
            return True
        except TelegramAPIError as e:
            logger.error(f"Failed to send message: {e}")
            return False
        except Exception as e:
            logger.error(f"Unexpected error sending message: {e}")
            return False

    async def close(self):
        """Close bot session. No-op when using cached shared instance."""
        if not self._is_shared:
            await self.bot.session.close()
