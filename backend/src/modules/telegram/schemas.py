"""Telegram module Pydantic schemas."""
from pydantic import BaseModel
from typing import Optional


class InviteLinkResponse(BaseModel):
    """Invite link response schema."""
    invite_link: str
    expires_at: Optional[int] = None


class ChannelAccessRequest(BaseModel):
    """Channel access request schema."""
    user_id: str
    action: str  # 'add' or 'remove'
