"""System settings module API routes."""
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from typing import Dict

from ...core.db import get_db
from ...core.security import require_admin_user
from .service import SystemSettingService
from .schemas import SettingResponse, SettingUpdate

router = APIRouter()

# Keys that must only be accessible via /api/admin/settings
SENSITIVE_KEYS = frozenset({
    "TELEGRAM_BOT_TOKEN",
    "BOT_API_SECRET",
    "YOOKASSA_SECRET_KEY",
    "SECRET_KEY",
})


def _filter_sensitive(settings: Dict[str, SettingResponse]) -> Dict[str, SettingResponse]:
    """Remove sensitive settings from response."""
    return {k: v for k, v in settings.items() if k not in SENSITIVE_KEYS}


@router.get("", response_model=Dict[str, SettingResponse])
async def get_settings(
    db: AsyncSession = Depends(get_db),
):
    """Get all settings (sensitive keys excluded). Use /api/admin/settings for full access."""
    service = SystemSettingService(db)
    all_settings = await service.get_settings()
    return _filter_sensitive(all_settings)


@router.get("/{key}", response_model=SettingResponse)
async def get_setting(
    key: str,
    db: AsyncSession = Depends(get_db),
):
    """Get setting by key. Sensitive keys return 404; use /api/admin/settings for full access."""
    if key in SENSITIVE_KEYS:
        raise HTTPException(status_code=404, detail="Setting not found")
    service = SystemSettingService(db)
    setting = await service.get_setting(key)
    if not setting:
        raise HTTPException(status_code=404, detail="Setting not found")
    return setting


# Critical security settings that cannot be modified at runtime
_PROTECTED_SETTINGS = frozenset({"SECRET_KEY", "BOT_API_SECRET"})


@router.patch("/{key}", response_model=SettingResponse)
async def update_setting(
    key: str,
    setting_data: SettingUpdate,
    admin_user=Depends(require_admin_user),
    db: AsyncSession = Depends(get_db),
):
    """Update setting (admin only)."""
    if key in _PROTECTED_SETTINGS:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="This setting cannot be modified at runtime. Change environment variables and restart the server.",
        )
    service = SystemSettingService(db)
    return await service.update_setting(key, setting_data)
