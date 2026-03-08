"""
Subscription handlers.
"""
from aiogram import Dispatcher
from aiogram.types import CallbackQuery

# TODO: Implement handlers


async def show_subscription_status(callback: CallbackQuery):
    """Show subscription status."""
    # TODO: Implement
    await callback.answer("Подписка активна")


async def show_tariffs(callback: CallbackQuery):
    """Show subscription tariffs."""
    # TODO: Implement
    await callback.answer("Тарифы")


def register_subscription_handlers(dp: Dispatcher) -> None:
    """Register subscription handlers."""
    # TODO: Register callback handlers
    pass
