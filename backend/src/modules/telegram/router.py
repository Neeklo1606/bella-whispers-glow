"""Telegram module API routes."""
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from pydantic import BaseModel

from ...core.db import get_db
from ...core.security import get_current_user_id
from ...core.security.bot_auth import verify_bot_secret
from .service import TelegramService
from .schemas import InviteLinkResponse, ChannelAccessRequest
from ..subscriptions.repository import SubscriptionRepository
from ..users.repository import UserRepository
from .bot_service import TelegramBotService
from ..channel_logs.service import ChannelAccessLogService
from ..channel_logs.models import ChannelAccessEventType

router = APIRouter()


class RevokeInviteLinkRequest(BaseModel):
    """Request to revoke invite link."""
    telegram_id: int


@router.get("/invite-link", response_model=InviteLinkResponse)
async def get_invite_link(
    user_id: str = Depends(get_current_user_id),
    db: AsyncSession = Depends(get_db),
):
    """Get invite link for Telegram channel."""
    service = TelegramService(db)
    link = await service.generate_invite_link(user_id)
    if not link:
        raise HTTPException(
            status_code=403, detail="Active subscription required"
        )
    return link


@router.post("/revoke-invite-link")
async def revoke_invite_link(
    request: RevokeInviteLinkRequest,
    db: AsyncSession = Depends(get_db),
    _: str = Depends(verify_bot_secret),
):
    """
    Revoke invite link when user joins channel.
    Called by bot when chat_member update is received.
    """
    try:
        # Find user by telegram_id
        user_repository = UserRepository(db)
        user = await user_repository.get_by_telegram_id(request.telegram_id)
        
        if not user:
            return {"success": False, "message": "User not found"}
        
        # Find active subscription
        subscription_repository = SubscriptionRepository(db)
        subscription = await subscription_repository.get_active_by_user_id(user.id)
        
        if not subscription or not subscription.telegram_invite_link:
            return {"success": False, "message": "No active invite link found"}
        
        # Revoke invite link
        bot_service = await TelegramBotService.create(db)
        revoked = await bot_service.revoke_chat_invite_link(
            subscription.telegram_invite_link
        )
        
        if revoked:
            # Clear invite link from subscription
            await subscription_repository.update(
                subscription.id,
                {
                    "telegram_invite_link": None,
                    "telegram_invite_link_expires": None,
                },
            )
            
            # Log events
            log_service = ChannelAccessLogService(db)
            await log_service.log_event(
                user_id=user.id,
                event_type=ChannelAccessEventType.INVITE_REVOKED,
                telegram_id=user.telegram_id,
                subscription_id=subscription.id,
            )
            # Log join event (user joined channel)
            await log_service.log_event(
                user_id=user.id,
                event_type=ChannelAccessEventType.JOIN,
                telegram_id=user.telegram_id,
                subscription_id=subscription.id,
            )
            
            await bot_service.close()
            return {"success": True, "message": "Invite link revoked"}
        
        await bot_service.close()
        return {"success": False, "message": "Failed to revoke invite link"}
    
    except Exception as e:
        return {"success": False, "message": str(e)}


@router.post("/channel-access")
async def manage_channel_access(
    request: ChannelAccessRequest,
    db: AsyncSession = Depends(get_db),
):
    """Manage user access to channel (admin only)."""
    service = TelegramService(db)
    if request.action == "add":
        result = await service.add_user_to_channel(request)
    else:
        result = await service.remove_user_from_channel(request)
    return {"success": result}
