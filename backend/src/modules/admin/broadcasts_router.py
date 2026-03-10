"""Admin broadcasts: send messages to Telegram bot users."""
from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from typing import List, Optional

from ...core.db import get_db
from ...core.security import require_admin_user
from ...modules.users.models import User
from ...modules.users.repository import UserRepository
from ...modules.telegram.bot_service import TelegramBotService

from sqlalchemy.ext.asyncio import AsyncSession

router = APIRouter()


class BroadcastSendRequest(BaseModel):
    """Request to send broadcast to users."""
    text: str
    media_type: Optional[str] = None  # "photo" | "video"
    media_url: Optional[str] = None
    target: str = "all"  # "all" | "selected"
    user_ids: Optional[List[str]] = None  # when target=selected


class BroadcastSendResponse(BaseModel):
    """Response after broadcast send."""
    sent: int
    failed: int
    total: int
    errors: List[str] = []


@router.post("/send", response_model=BroadcastSendResponse)
async def admin_send_broadcast(
    data: BroadcastSendRequest,
    admin_user: User = Depends(require_admin_user),
    db: AsyncSession = Depends(get_db),
):
    """
    Send message (text, photo, or video) to users.
    target=all: all users with telegram_id
    target=selected: users in user_ids list
    """
    if not data.text.strip():
        raise HTTPException(status_code=400, detail="Текст сообщения обязателен")

    user_repo = UserRepository(db)
    if data.target == "all":
        users = await user_repo.get_all_with_telegram()
    elif data.target == "selected" and data.user_ids:
        from uuid import UUID
        try:
            ids = [UUID(uid) for uid in data.user_ids]
        except ValueError:
            raise HTTPException(status_code=400, detail="Некорректные ID пользователей")
        users = await user_repo.get_by_ids(ids)
    else:
        raise HTTPException(status_code=400, detail="Укажите target=all или target=selected с user_ids")

    if not users:
        return BroadcastSendResponse(sent=0, failed=0, total=0, errors=["Нет пользователей с Telegram для рассылки"])

    bot_service = await TelegramBotService.create(db)
    sent = 0
    failed = 0
    errors = []
    for user in users:
        if not user.telegram_id:
            continue
        try:
            ok = await bot_service.send_to_user(
                user_id=user.telegram_id,
                text=data.text,
                media_type=data.media_type,
                media_url=data.media_url,
            )
            if ok:
                sent += 1
            else:
                failed += 1
                errors.append(f"User {user.id}: send failed")
        except Exception as e:
            failed += 1
            errors.append(f"User {user.id}: {str(e)}")
    await bot_service.close()

    return BroadcastSendResponse(
        sent=sent,
        failed=failed,
        total=len(users),
        errors=errors[:20],
    )
