"""
Start command handler.
"""
from aiogram import Dispatcher
from aiogram.filters import Command
from aiogram.types import Message

from ..keyboards.main_menu import get_main_menu_keyboard


async def cmd_start(message: Message):
    """Handle /start command. Main menu: Тарифы, Подписка, Договор оферты, Обратная связь."""
    await message.answer(
        "Добро пожаловать! Выберите действие:",
        reply_markup=get_main_menu_keyboard(),
    )


async def cmd_help(message: Message):
    """Handle /help command."""
    await message.answer("Помощь")


def register_start_handlers(dp: Dispatcher) -> None:
    """Register start handlers."""
    dp.message.register(cmd_start, Command("start"))
    dp.message.register(cmd_help, Command("help"))
