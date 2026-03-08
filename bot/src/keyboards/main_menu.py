"""
Main menu keyboard.
"""
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton

# TODO: Implement keyboards


def get_main_menu_keyboard() -> InlineKeyboardMarkup:
    """Get main menu keyboard."""
    keyboard = InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(text="📋 Моя подписка", callback_data="subscription"),
            ],
            [
                InlineKeyboardButton(text="💳 Тарифы", callback_data="tariffs"),
            ],
            [
                InlineKeyboardButton(text="🔗 Mini App", web_app={"url": "https://app.bellahasias.ru"}),
            ],
            [
                InlineKeyboardButton(text="📱 Открыть канал", callback_data="channel"),
            ],
        ]
    )
    return keyboard
