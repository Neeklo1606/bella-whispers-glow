"""
Subscription handlers: tariffs, subscription status.
"""
import logging
from aiogram import Dispatcher, F
from aiogram.types import CallbackQuery
from datetime import datetime

from ..services.api_client import get_api_client
from ..keyboards.main_menu import (
    get_main_menu_keyboard,
    get_tariff_keyboard,
    get_tariff_agreement_keyboard,
    get_subscription_no_keyboard,
)
from ..utils.runtime_settings import get as get_runtime

logger = logging.getLogger(__name__)


def _format_duration(days: int) -> str:
    """Format duration_days to Russian (1 месяц, 3 месяца, ...)."""
    if days == 30:
        return "1 месяц"
    if days == 90:
        return "3 месяца"
    if days == 365:
        return "1 год"
    return f"{days} дн."


def _format_end_date(iso_date: str | None) -> str:
    """Format end_date for display."""
    if not iso_date:
        return "—"
    try:
        dt = datetime.fromisoformat(iso_date.replace("Z", "+00:00"))
        return dt.strftime("%d.%m.%Y")
    except Exception:
        return iso_date


async def show_tariff_agreement(callback: CallbackQuery):
    """First step: agreement text + Открыть договор оферты."""
    await callback.answer()
    offer_url = get_runtime("OFFER_URL") or "https://bellahasias.ru/privacy"
    text = (
        "Оплачивая подписку, вы соглашаетесь с договором оферты "
        "и обработкой персональных данных."
    )
    keyboard = get_tariff_agreement_keyboard(offer_url)
    try:
        await callback.message.edit_text(text, reply_markup=keyboard)
    except Exception as e:
        logger.warning("edit_text failed: %s", e)
        await callback.message.answer(text, reply_markup=keyboard)


async def show_tariffs(callback: CallbackQuery):
    """Show tariffs: plans + Оплата российской картой / Telegram Stars / Назад."""
    await callback.answer()
    miniapp_url = get_runtime("MINIAPP_URL") or "https://app.bellahasias.ru"
    api = get_api_client()
    plans = await api.get_plans()
    if not plans:
        text = "Тарифы временно недоступны. Обратитесь к администратору."
        keyboard = get_main_menu_keyboard()
    else:
        lines = []
        for p in plans:
            dur = _format_duration(p.get("duration_days", 30))
            price = p.get("first_month_price") or p.get("price", 0)
            lines.append(f"{dur} — {int(price)} ₽")
        text = "Тарифы:\n\n" + "\n".join(lines)
        keyboard = get_tariff_keyboard(plans, miniapp_url)
    try:
        await callback.message.edit_text(text, reply_markup=keyboard)
    except Exception as e:
        logger.warning("edit_text failed: %s", e)
        await callback.message.answer(text, reply_markup=keyboard)


async def show_subscription_status(callback: CallbackQuery):
    """Show subscription status: check via API, show date or offer tariffs."""
    await callback.answer()
    user = callback.from_user
    if not user:
        text = "Не удалось определить пользователя."
        keyboard = get_main_menu_keyboard()
    else:
        api = get_api_client()
        data = await api.get_subscription_by_telegram(user.id)
        sub = (data or {}).get("subscription") if data else None
        if sub and sub.get("status") == "active":
            end_date = _format_end_date(sub.get("end_date"))
            text = f"Ваша подписка активна.\nДействует до: {end_date}"
            keyboard = get_main_menu_keyboard()
        else:
            text = "У вас нет активной подписки.\nПерейдите в тарифы, чтобы оформить подписку."
            keyboard = get_main_menu_keyboard()  # with tariffs button
            from ..keyboards.main_menu import get_subscription_no_keyboard
            keyboard = get_subscription_no_keyboard()
    try:
        await callback.message.edit_text(text, reply_markup=keyboard)
    except Exception:
        await callback.message.answer(text, reply_markup=keyboard)


def register_subscription_handlers(dp: Dispatcher) -> None:
    """Register subscription handlers."""
    dp.callback_query.register(show_tariff_agreement, F.data == "tariffs")
    dp.callback_query.register(show_tariffs, F.data == "tariffs_plans")
    dp.callback_query.register(show_subscription_status, F.data == "subscription")
