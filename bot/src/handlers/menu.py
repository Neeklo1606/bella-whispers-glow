"""
Menu handlers.
"""
from aiogram import Dispatcher
from aiogram.types import CallbackQuery

# TODO: Implement handlers


async def open_mini_app(callback: CallbackQuery):
    """Open Mini App."""
    # TODO: Implement
    await callback.answer("Mini App")


async def open_channel(callback: CallbackQuery):
    """Open Telegram channel."""
    # TODO: Implement
    await callback.answer("Канал")


def register_menu_handlers(dp: Dispatcher) -> None:
    """Register menu handlers."""
    # TODO: Register callback handlers
    pass
