"""Schedule module repository."""
from sqlalchemy.ext.asyncio import AsyncSession
from typing import List

# No ScheduleEvent model - schedule uses broadcasts.
# Return empty list to prevent runtime crashes in ScheduleService.


class ScheduleRepository:
    """Repository for schedule operations."""

    def __init__(self, db: AsyncSession):
        self.db = db

    async def get_upcoming_events(self) -> List:
        """Get upcoming schedule events. No model yet - returns empty list."""
        return []

    async def get_past_events(self) -> List:
        """Get past schedule events. No model yet - returns empty list."""
        return []
