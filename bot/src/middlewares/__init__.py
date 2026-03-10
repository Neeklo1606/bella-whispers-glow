"""
Register all middlewares.
"""
from aiogram import Dispatcher

from .register_user import RegisterUserMiddleware


def register_middlewares(dp: Dispatcher) -> None:
    """Register all middlewares."""
    dp.message.middleware(RegisterUserMiddleware())
    dp.callback_query.middleware(RegisterUserMiddleware())
