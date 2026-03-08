"""System settings module Pydantic schemas."""
from pydantic import BaseModel
from typing import Any, Optional


class SettingResponse(BaseModel):
    """Setting response schema."""
    key: str
    value: Any
    description: Optional[str] = None


class SettingUpdate(BaseModel):
    """Setting update schema."""
    value: Any
