"""
Main menu keyboard.
"""
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton

from ..utils.runtime_settings import get as get_runtime


def get_main_menu_keyboard() -> InlineKeyboardMarkup:
    """Get main menu keyboard: Тарифы, Подписка, Договор оферты, Обратная связь."""
    offer_url = get_runtime("OFFER_URL")
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [InlineKeyboardButton(text="💳 Тарифы", callback_data="tariffs")],
            [InlineKeyboardButton(text="📋 Подписка", callback_data="subscription")],
            [
                InlineKeyboardButton(
                    text="📄 Договор оферты",
                    url=offer_url,
                ),
            ],
            [InlineKeyboardButton(text="💬 Обратная связь", callback_data="support")],
        ]
    )


def get_back_keyboard() -> InlineKeyboardMarkup:
    """Back to main menu button."""
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [InlineKeyboardButton(text="◀️ Назад", callback_data="main_menu")],
        ]
    )


def get_tariff_keyboard(miniapp_url: str) -> InlineKeyboardMarkup:
    """Buttons: Оплатить, Назад."""
    pay_url = f"{miniapp_url}/pricing"
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [InlineKeyboardButton(text="💳 Оплатить", url=pay_url)],
            [InlineKeyboardButton(text="◀️ Назад", callback_data="main_menu")],
        ]
    )
