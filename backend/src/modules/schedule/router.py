"""Schedule module API routes."""
from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from typing import List

from ...core.db import get_db
from .service import ScheduleService
from .schemas import ScheduleEventResponse

router = APIRouter()


@router.get("/upcoming", response_model=List[ScheduleEventResponse])
async def get_upcoming_events(
    db: AsyncSession = Depends(get_db),
):
    """Get upcoming schedule events."""
    service = ScheduleService(db)
    return await service.get_upcoming_events()


@router.get("/past", response_model=List[ScheduleEventResponse])
async def get_past_events(
    db: AsyncSession = Depends(get_db),
):
    """Get past schedule events."""
    service = ScheduleService(db)
    return await service.get_past_events()
