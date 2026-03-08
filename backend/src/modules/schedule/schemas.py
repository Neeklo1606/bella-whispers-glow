"""Schedule module Pydantic schemas."""
from pydantic import BaseModel
from typing import Optional
from datetime import datetime


class ScheduleEventResponse(BaseModel):
    """Schedule event response schema."""
    id: str
    title: str
    description: Optional[str] = None
    date: datetime
    type: str
    created_at: datetime

    class Config:
        from_attributes = True
