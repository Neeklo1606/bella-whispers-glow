"""
Subscription handlers: tariffs, subscription status.
"""
import logging
from aiogram import Dispatcher, F
from aiogram.types import CallbackQuery

from ..services.api_client import get_api_client
from ..keyboards.main_menu import get_main_menu_keyboard, get_tariff_keyboard
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


async def show_tariffs(callback: CallbackQuery):
    """Show tariffs: GET /api/subscriptions/plans, display, buttons Оплатить/Назад."""
    await callback.answer()
    miniapp_url = get_runtime("MINIAPP_URL")
    api = get_api_client()
    plans = await api.get_plans()
    if not plans:
        text = "Тарифы временно недоступны."
    else:
        lines = []
        for p in plans:
            dur = _format_duration(p.get("duration_days", 30))
            price = p.get("price", 0)
            lines.append(f"{dur} — {int(price)} ₽")
        text = "Тарифы:\n\n" + "\n".join(lines)
    try:
        await callback.message.edit_text(
            text,
            reply_markup=get_tariff_keyboard(config.MINIAPP_URL),
        )
    except Exception as e:
        logger.warning("edit_text failed, sending new message: %s", e)
        await callback.message.answer(text, reply_markup=get_tariff_keyboard(miniapp_url))


async def show_subscription_status(callback: CallbackQuery):
    """Show subscription status. No auth -> suggest Mini App."""
    await callback.answer()
    text = (
        "Информация о подписке доступна в Mini App.\n"
        "Откройте приложение, чтобы посмотреть статус подписки."
    )
    keyboard = get_main_menu_keyboard()
    try:
        await callback.message.edit_text(text, reply_markup=keyboard)
    except Exception:
        await callback.message.answer(text, reply_markup=keyboard)


def register_subscription_handlers(dp: Dispatcher) -> None:
    """Register subscription handlers."""
    dp.callback_query.register(show_tariffs, F.data == "tariffs")
    dp.callback_query.register(show_subscription_status, F.data == "subscription")
