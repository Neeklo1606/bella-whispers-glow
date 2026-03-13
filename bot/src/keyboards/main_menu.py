"""
Main menu keyboard.
"""
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton, WebAppInfo

from ..utils.runtime_settings import get as get_runtime


def get_main_menu_keyboard() -> InlineKeyboardMarkup:
    """Get main menu keyboard: Тарифы, Подписка, Договор оферты, Обратная связь."""
    offer_url = get_runtime("OFFER_URL") or "https://bellahasias.ru/privacy"
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


def get_tariff_agreement_keyboard(offer_url: str) -> InlineKeyboardMarkup:
    """Agreement step: Открыть договор оферты, Далее к тарифам, Назад."""
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [InlineKeyboardButton(text="📄 Открыть договор оферты", url=offer_url)],
            [InlineKeyboardButton(text="➡️ Далее к тарифам", callback_data="tariffs_plans")],
            [InlineKeyboardButton(text="◀️ Назад", callback_data="main_menu")],
        ]
    )


def get_tariff_keyboard(plans: list, miniapp_url: str) -> InlineKeyboardMarkup:
    """Buttons: Оплатить подписку (Web App → Mini App + YooKassa), Назад."""
    miniapp_pay_url = f"{miniapp_url.rstrip('/')}/pricing"
    buttons = [
        [
            InlineKeyboardButton(
                text="💳 Оплатить подписку",
                web_app=WebAppInfo(url=miniapp_pay_url),
            ),
        ],
        [InlineKeyboardButton(text="◀️ Назад", callback_data="tariffs")],
    ]
    return InlineKeyboardMarkup(inline_keyboard=buttons)


def get_subscription_no_keyboard() -> InlineKeyboardMarkup:
    """When no subscription: Тарифы + Назад."""
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [InlineKeyboardButton(text="💳 Тарифы", callback_data="tariffs")],
            [InlineKeyboardButton(text="◀️ Назад", callback_data="main_menu")],
        ]
    )
