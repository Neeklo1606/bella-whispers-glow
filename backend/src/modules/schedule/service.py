"""Schedule module service."""
from sqlalchemy.ext.asyncio import AsyncSession
from typing import List

from .repository import ScheduleRepository
from .schemas import ScheduleEventResponse


class ScheduleService:
    """Service for schedule operations."""

    def __init__(self, db: AsyncSession):
        self.repository = ScheduleRepository(db)

    async def get_upcoming_events(self) -> List[ScheduleEventResponse]:
        """Get upcoming events."""
        # TODO: Implement
        pass

    async def get_past_events(self) -> List[ScheduleEventResponse]:
        """Get past events."""
        # TODO: Implement
        pass
