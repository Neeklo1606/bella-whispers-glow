"""
Subscription handlers: tariffs, subscription status.
TZ: tariffs/subscription depend on user status; days_left recalculated each time.
"""
import logging
from aiogram import Dispatcher, F
from aiogram.types import CallbackQuery
from datetime import datetime, timezone

from ..services.api_client import get_api_client
from ..keyboards.main_menu import (
    get_main_menu_keyboard,
    get_tariff_keyboard,
    get_tariff_agreement_keyboard,
    get_tariff_keyboard_when_active,
    get_subscription_no_keyboard,
    get_subscription_active_keyboard,
)
from ..utils.runtime_settings import get as get_runtime

logger = logging.getLogger(__name__)


def _days_left(end_date_iso: str | None) -> int:
    """Calculate days until end_date. Returns 0 if past or invalid."""
    if not end_date_iso:
        return 0
    try:
        dt = datetime.fromisoformat(end_date_iso.replace("Z", "+00:00"))
        now = datetime.now(timezone.utc)
        delta = (dt.replace(tzinfo=timezone.utc) if dt.tzinfo is None else dt) - now
        return max(0, delta.days)
    except Exception:
        return 0


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
    """First step: agreement text from MSG_TARIFFS_INTRO + Открыть договор оферты."""
    await callback.answer()
    offer_url = get_runtime("OFFER_URL") or "https://bellahasias.ru/privacy"
    text = get_runtime("MSG_TARIFFS_INTRO") or (
        "Оплачивая подписку, вы соглашаетесь с договором оферты и обработкой персональных данных."
    )
    keyboard = get_tariff_agreement_keyboard(offer_url)
    try:
        await callback.message.edit_text(text, reply_markup=keyboard)
    except Exception as e:
        logger.warning("edit_text failed: %s", e)
        await callback.message.answer(text, reply_markup=keyboard)


async def show_tariffs(callback: CallbackQuery):
    """Show tariffs. If active subscription: MSG_TARIFFS_ACTIVE + Продлить/Ссылка/Оферта. Else: plans + оплата."""
    await callback.answer()
    user = callback.from_user
    miniapp_url = get_runtime("MINIAPP_URL") or "https://app.bellahasias.ru"
    offer_url = get_runtime("OFFER_URL") or "https://bellahasias.ru/privacy"
    api = get_api_client()
    if user:
        data = await api.get_subscription_by_telegram(user.id)
        sub = (data or {}).get("subscription") if data else None
        if sub and sub.get("status") == "active":
            end_iso = sub.get("end_date")
            end_str = _format_end_date(end_iso)
            days = _days_left(end_iso)
            tpl = get_runtime("MSG_TARIFFS_ACTIVE") or "У вас активная подписка.\nДействует до: {{end_date}}\nОсталось дней: {{days_left}}\nПри необходимости вы можете продлить подписку заранее."
            text = tpl.replace("{{end_date}}", end_str).replace("{{days_left}}", str(days))
            keyboard = get_tariff_keyboard_when_active(miniapp_url, offer_url)
            try:
                await callback.message.edit_text(text, reply_markup=keyboard)
            except Exception as e:
                logger.warning("edit_text failed: %s", e)
                await callback.message.answer(text, reply_markup=keyboard)
            return
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
    """Show subscription: active (date, days_left, ссылка, продлить) or none (предложить тарифы)."""
    await callback.answer()
    user = callback.from_user
    miniapp_url = get_runtime("MINIAPP_URL") or "https://app.bellahasias.ru"
    if not user:
        text = "Не удалось определить пользователя."
        keyboard = get_main_menu_keyboard()
    else:
        api = get_api_client()
        data = await api.get_subscription_by_telegram(user.id)
        sub = (data or {}).get("subscription") if data else None
        if sub and sub.get("status") == "active":
            end_iso = sub.get("end_date")
            end_str = _format_end_date(end_iso)
            days = _days_left(end_iso)
            tpl = get_runtime("MSG_SUBSCRIPTION_ACTIVE") or "Ваша подписка активна до {{end_date}}.\nОсталось {{days_left}} дн."
            text = tpl.replace("{{end_date}}", end_str).replace("{{days_left}}", str(days))
            keyboard = get_subscription_active_keyboard(miniapp_url)
        else:
            text = get_runtime("MSG_SUBSCRIPTION_NONE") or "У вас нет активной подписки.\nПерейти к покупке?"
            keyboard = get_subscription_no_keyboard()
    try:
        await callback.message.edit_text(text, reply_markup=keyboard)
    except Exception:
        await callback.message.answer(text, reply_markup=keyboard)


async def handle_get_channel_link(callback: CallbackQuery):
    """User clicked 'Получить ссылку в канал' - fetch invite link from API, send to user."""
    await callback.answer()
    user = callback.from_user
    if not user:
        return
    api = get_api_client()
    result = await api.get_invite_link(user.id)
    if result and result.get("invite_link"):
        link = result["invite_link"]
        try:
            await callback.message.answer(
                f"🔗 Ссылка для доступа в закрытый канал:\n{link}",
                reply_markup=get_main_menu_keyboard(),
            )
        except Exception as e:
            logger.warning("send link failed: %s", e)
    else:
        text = "У вас нет активной подписки. Оформите подписку, чтобы получить доступ."
        try:
            await callback.message.answer(text, reply_markup=get_subscription_no_keyboard())
        except Exception:
            pass


def register_subscription_handlers(dp: Dispatcher) -> None:
    """Register subscription handlers."""
    dp.callback_query.register(show_tariff_agreement, F.data == "tariffs")
    dp.callback_query.register(show_tariffs, F.data == "tariffs_plans")
    dp.callback_query.register(show_subscription_status, F.data == "subscription")
    dp.callback_query.register(handle_get_channel_link, F.data == "get_channel_link")
