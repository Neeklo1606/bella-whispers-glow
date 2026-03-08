"""Users module Pydantic schemas."""
from pydantic import BaseModel, EmailStr
from typing import Optional
from datetime import datetime

from .enums import UserRole


class UserBase(BaseModel):
    """Base user schema."""
    telegram_id: Optional[int] = None
    username: Optional[str] = None
    first_name: Optional[str] = None
    last_name: Optional[str] = None
    avatar_url: Optional[str] = None
    email: Optional[EmailStr] = None
    role: UserRole = UserRole.USER


class UserCreate(BaseModel):
    """User creation schema."""
    telegram_id: Optional[int] = None
    username: Optional[str] = None
    first_name: Optional[str] = None
    last_name: Optional[str] = None
    email: Optional[EmailStr] = None
    password: Optional[str] = None  # Plain password for admin users
    role: UserRole = UserRole.USER


class UserUpdate(BaseModel):
    """User update schema."""
    username: Optional[str] = None
    first_name: Optional[str] = None
    last_name: Optional[str] = None
    email: Optional[EmailStr] = None
    avatar_url: Optional[str] = None
    password: Optional[str] = None  # Plain password for update
    role: Optional[UserRole] = None


class UserResponse(BaseModel):
    """User response schema."""
    id: str
    telegram_id: Optional[int] = None
    username: Optional[str] = None
    first_name: Optional[str] = None
    last_name: Optional[str] = None
    avatar_url: Optional[str] = None
    email: Optional[str] = None
    role: UserRole
    is_admin: bool
    is_telegram_user: bool
    is_admin_user: bool
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True
