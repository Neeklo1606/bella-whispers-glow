"""Broadcasts module Pydantic schemas."""
from pydantic import BaseModel
from typing import Optional, List
from datetime import datetime


class BroadcastCreate(BaseModel):
    """Broadcast creation schema."""
    title: str
    content: str
    media_url: Optional[str] = None
    scheduled_at: Optional[datetime] = None


class BroadcastResponse(BaseModel):
    """Broadcast response schema."""
    id: str
    created_by: str
    title: str
    content: str
    media_url: Optional[str] = None
    scheduled_at: Optional[datetime] = None
    sent_at: Optional[datetime] = None
    status: str
    created_at: datetime

    class Config:
        from_attributes = True
