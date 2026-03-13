"""
Telegram bot handlers for channel member updates.
"""
import logging
import httpx
from aiogram import Dispatcher
from aiogram.filters import ChatMemberUpdatedFilter, KICKED, LEFT, MEMBER
from aiogram.types import ChatMemberUpdated
from aiogram.enums import ChatMemberStatus

from ..utils.config import get_bot_config

logger = logging.getLogger(__name__)
config = get_bot_config()


async def handle_chat_member_update(update: ChatMemberUpdated) -> None:
    """
    Handle chat member updates (user joins/leaves channel).
    
    Args:
        update: Chat member update event
    """
    # Only process updates for the channel
    if str(update.chat.id) != config.CHANNEL_ID:
        return

    # Only process when user becomes a member (was not a member before)
    old_status = update.old_chat_member.status
    new_status = update.new_chat_member.status
    
    # Check if user transitioned from non-member to member
    if old_status in [ChatMemberStatus.MEMBER, ChatMemberStatus.ADMINISTRATOR, ChatMemberStatus.CREATOR]:
        return
    
    if new_status not in [ChatMemberStatus.MEMBER, ChatMemberStatus.ADMINISTRATOR, ChatMemberStatus.CREATOR]:
        return

    user_id = update.new_chat_member.user.id
    
    try:
        # Call backend API to revoke invite link
        headers = {}
        if config.BOT_API_SECRET:
            headers["X-Bot-Secret"] = config.BOT_API_SECRET
        
        async with httpx.AsyncClient() as client:
            response = await client.post(
                f"{config.API_BASE_URL}/api/telegram/revoke-invite-link",
                json={"telegram_id": user_id},
                headers=headers,
                timeout=10.0,
            )
            
            if response.status_code == 200:
                logger.info(f"Revoked invite link for user {user_id} after joining channel")
            else:
                logger.warning(f"Failed to revoke invite link for user {user_id}: {response.status_code}")
    
    except Exception as e:
        logger.error(f"Error handling chat member update for user {user_id}: {e}")


def register_channel_handlers(dp: Dispatcher) -> None:
    """Register channel handlers."""
    dp.chat_member.register(
        handle_chat_member_update,
        ChatMemberUpdatedFilter(member_status_changed=(KICKED | LEFT) >> MEMBER),
    )
