"""
Payment handlers.
"""
from aiogram import Dispatcher
from aiogram.types import CallbackQuery

# TODO: Implement handlers


async def process_payment(callback: CallbackQuery):
    """Process payment."""
    # TODO: Implement
    await callback.answer("Оплата")


def register_payment_handlers(dp: Dispatcher) -> None:
    """Register payment handlers."""
    # TODO: Register callback handlers
    pass
