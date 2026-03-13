"""
User-related enums.
"""
import enum


class UserRole(str, enum.Enum):
    """User role enum."""

    USER = "user"
    ADMIN = "admin"
    SUPER_ADMIN = "super_admin"
