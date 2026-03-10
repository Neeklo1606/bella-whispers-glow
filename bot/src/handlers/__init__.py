"""
Register all handlers.
"""
from aiogram import Dispatcher

from .start import register_start_handlers
from .subscription import register_subscription_handlers
from .payment import register_payment_handlers
from .menu import register_menu_handlers
from .text_messages import register_text_handlers
from .channel import register_channel_handlers


def register_handlers(dp: Dispatcher) -> None:
    """Register all handlers."""
    register_start_handlers(dp)
    register_subscription_handlers(dp)
    register_payment_handlers(dp)
    register_menu_handlers(dp)
    register_text_handlers(dp)  # feedback + payment email
    register_channel_handlers(dp)
