"""Middleware to register bot users in backend DB on every interaction."""
import logging
from aiogram import BaseMiddleware
from aiogram.types import Message, CallbackQuery, TelegramObject

from ..services.api_client import get_api_client

logger = logging.getLogger(__name__)


class RegisterUserMiddleware(BaseMiddleware):
    """Register user in backend on message or callback."""

    async def __call__(self, handler, event: TelegramObject, data: dict):
        user = None
        if isinstance(event, Message) and event.from_user:
            user = event.from_user
        elif isinstance(event, CallbackQuery) and event.from_user:
            user = event.from_user

        if user:
            try:
                api = get_api_client()
                await api.register_user(
                    telegram_id=user.id,
                    username=user.username or "",
                    first_name=user.first_name or "",
                    last_name=user.last_name or "",
                )
            except Exception as e:
                logger.debug("register_user failed: %s", e)

        return await handler(event, data)
