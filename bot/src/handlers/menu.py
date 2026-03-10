"""
Menu handlers: main menu, support.
"""
from aiogram import Dispatcher
from aiogram.types import CallbackQuery
from aiogram.filters import Text

from ..keyboards.main_menu import get_main_menu_keyboard
from ..utils.runtime_settings import get as get_runtime


async def back_to_main_menu(callback: CallbackQuery):
    """Edit message to main menu."""
    await callback.answer()
    text = "Выберите действие:"
    try:
        await callback.message.edit_text(text, reply_markup=get_main_menu_keyboard())
    except Exception:
        await callback.message.answer(text, reply_markup=get_main_menu_keyboard())


async def show_support(callback: CallbackQuery):
    """Show support / feedback info."""
    await callback.answer()
    support_username = get_runtime("SUPPORT_USERNAME")
    text = (
        "Обратная связь:\n\n"
        f"Напишите нам в Telegram: @{support_username}"
    )
    try:
        await callback.message.edit_text(
            text,
            reply_markup=get_main_menu_keyboard(),
        )
    except Exception:
        await callback.message.answer(text, reply_markup=get_main_menu_keyboard())


def register_menu_handlers(dp: Dispatcher) -> None:
    """Register menu handlers."""
    dp.callback_query.register(back_to_main_menu, Text("main_menu"))
    dp.callback_query.register(show_support, Text("support"))
