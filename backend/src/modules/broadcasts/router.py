"""Broadcasts module API routes."""
from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from typing import List

from ...core.db import get_db
from ...core.security import get_current_user_id
from .service import BroadcastService
from .schemas import BroadcastCreate, BroadcastResponse

router = APIRouter()


@router.post("", response_model=BroadcastResponse)
async def create_broadcast(
    broadcast_data: BroadcastCreate,
    user_id: str = Depends(get_current_user_id),
    db: AsyncSession = Depends(get_db),
):
    """Create broadcast (admin only)."""
    service = BroadcastService(db)
    return await service.create_broadcast(user_id, broadcast_data)


@router.get("", response_model=List[BroadcastResponse])
async def get_broadcasts(
    db: AsyncSession = Depends(get_db),
):
    """Get all broadcasts (admin only)."""
    service = BroadcastService(db)
    return await service.get_broadcasts()
