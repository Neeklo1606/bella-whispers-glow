"""
Menu handlers: main menu, support.
"""
from aiogram import Dispatcher, F
from aiogram.types import CallbackQuery

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
    """Обратная связь: Напишите ваш вопрос — сообщение пересылается владельцу."""
    await callback.answer()
    from ..utils.user_state import set_state
    if callback.from_user:
        set_state(callback.from_user.id, "awaiting_feedback")
    support_username = (get_runtime("SUPPORT_USERNAME") or "Bella_hasias").strip().lstrip("@")
    text = f"Напишите ваш вопрос.\n\nСообщение будет переслано @{support_username}"
    try:
        await callback.message.edit_text(
            text,
            reply_markup=get_main_menu_keyboard(),
        )
    except Exception:
        await callback.message.answer(text, reply_markup=get_main_menu_keyboard())


def register_menu_handlers(dp: Dispatcher) -> None:
    """Register menu handlers."""
    dp.callback_query.register(back_to_main_menu, F.data == "main_menu")
    dp.callback_query.register(show_support, F.data == "support")
