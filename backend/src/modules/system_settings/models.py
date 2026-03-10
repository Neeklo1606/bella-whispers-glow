"""
System settings module SQLAlchemy models.
"""
from sqlalchemy import Column, String, Text, Index
from sqlalchemy.dialects.postgresql import JSON

from ...core.db import BaseModel


class SystemSetting(BaseModel):
    """System setting model."""

    __tablename__ = "system_settings"

    key = Column(String(255), unique=True, nullable=False, index=True)
    value = Column(JSON, nullable=True)
    description = Column(Text, nullable=True)

    __table_args__ = (
        Index("idx_system_settings_key", "key"),
    )
