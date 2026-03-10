"""
Internal API for the Telegram bot to fetch its config (token, channel).
Only accessible from localhost.
"""
from fastapi import APIRouter, Request, HTTPException, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from ...core.db import get_db
from ...core.security.telegram import get_telegram_bot_token
from ..system_settings.service import SystemSettingService

router = APIRouter()
_DEFAULT_CHANNEL = "-1003802293810"


@router.get("/config")
async def get_bot_config(
    request: Request,
    db: AsyncSession = Depends(get_db),
):
    """
    Return bot token and channel for the Telegram bot process.
    Only from localhost (bot runs on same server).
    """
    client_host = request.client.host if request.client else ""
    if client_host not in ("127.0.0.1", "::1", "localhost"):
        raise HTTPException(status_code=403, detail="Forbidden")
    token = await get_telegram_bot_token(db)
    service = SystemSettingService(db)
    channel = await service.get("TELEGRAM_CHANNEL_ID") or _DEFAULT_CHANNEL
    return {"bot_token": token, "channel_id": channel, "api_base_url": ""}
