"""
Auth module Pydantic schemas.
"""
from pydantic import BaseModel, Field
from typing import Optional


class TelegramAuthData(BaseModel):
    """Telegram authentication data."""

    id: int
    first_name: str
    last_name: Optional[str] = None
    username: Optional[str] = None
    photo_url: Optional[str] = None
    auth_date: int
    hash: str


class TokenResponse(BaseModel):
    """Token response schema."""

    access_token: str
    refresh_token: str
    token_type: str = "bearer"


class LoginRequest(BaseModel):
    """Login request schema."""

    email: str = Field(..., description="User email")
    password: str = Field(..., min_length=8, description="User password")


class RefreshTokenRequest(BaseModel):
    """Refresh token request schema."""

    refresh_token: str = Field(..., description="Refresh token")


class AdminLoginRequest(BaseModel):
    """Admin login request schema."""

    email: str = Field(..., description="Admin email")
    password: str = Field(..., description="Admin password")


class AdminLoginResponse(BaseModel):
    """Admin login response schema."""

    access_token: str
    token_type: str = "bearer"
    user: dict


class TelegramInitDataRequest(BaseModel):
    """Telegram initData request schema."""

    initData: str = Field(..., description="Telegram WebApp initData string")


class TelegramAuthResponse(BaseModel):
    """Telegram authentication response schema."""

    access_token: str
    token_type: str = "bearer"
    user: dict
