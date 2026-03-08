"""
Start command handler.
"""
from aiogram import Dispatcher, F
from aiogram.filters import Command
from aiogram.types import Message

# TODO: Implement handlers
# from ..services.api_client import APIClient


async def cmd_start(message: Message):
    """Handle /start command."""
    # TODO: Implement
    await message.answer("Добро пожаловать!")


async def cmd_help(message: Message):
    """Handle /help command."""
    # TODO: Implement
    await message.answer("Помощь")


def register_start_handlers(dp: Dispatcher) -> None:
    """Register start handlers."""
    dp.message.register(cmd_start, Command("start"))
    dp.message.register(cmd_help, Command("help"))
