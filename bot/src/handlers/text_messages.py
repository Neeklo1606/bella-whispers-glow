"""
Unified text message handler: feedback forward, payment email.
"""
import re
import logging
from aiogram import Dispatcher, F
from aiogram.types import Message, InlineKeyboardMarkup, InlineKeyboardButton

from ..services.api_client import get_api_client
from ..keyboards.main_menu import get_main_menu_keyboard
from ..utils.runtime_settings import get as get_runtime
from ..utils.user_state import get_state, pop_state

logger = logging.getLogger(__name__)
EMAIL_RE = re.compile(r"^[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+$")


async def handle_text_message(message: Message):
    """Route text by user state: awaiting_feedback -> forward, awaiting_email -> payment."""
    user = message.from_user
    if not user:
        return
    state = get_state(user.id)
    if not state:
        return

    if state.get("state") == "awaiting_feedback":
        pop_state(user.id)
        support_username = (get_runtime("SUPPORT_USERNAME") or "Bella_hasias").strip().lstrip("@")
        target = f"@{support_username}"
        try:
            await message.forward(chat_id=target)
            await message.answer(
                "Ваше сообщение переслано. Мы ответим в ближайшее время.",
                reply_markup=get_main_menu_keyboard(),
            )
        except Exception as e:
            logger.warning("Failed to forward to %s: %s", target, e)
            await message.answer(
                f"Не удалось переслать. Напишите напрямую: {target}",
                reply_markup=get_main_menu_keyboard(),
            )
        return

    if state.get("state") == "awaiting_email":
        email = (message.text or "").strip()
        if not EMAIL_RE.match(email):
            await message.answer("Пожалуйста, введите корректный email.")
            return
        plan_id = state.get("plan_id", "")
        pop_state(user.id)
        if not plan_id:
            await message.answer("Ошибка. Начните заново из меню Тарифы.", reply_markup=get_main_menu_keyboard())
            return
        api = get_api_client()
        try:
            result = await api.create_payment_from_bot(
                telegram_id=user.id,
                plan_id=plan_id,
                email=email,
                first_name=user.first_name or "",
                last_name=user.last_name or "",
                username=user.username or "",
            )
        except Exception as e:
            logger.exception("create_payment_from_bot failed: %s", e)
            await message.answer("Не удалось создать платёж. Попробуйте позже.", reply_markup=get_main_menu_keyboard())
            return
        if not result or not result.get("payment_url"):
            err = (result or {}).get("detail", "Не удалось создать платёж") if isinstance(result, dict) else "Ошибка"
            await message.answer(f"Ошибка: {err}", reply_markup=get_main_menu_keyboard())
            return
        pay_url = result["payment_url"]
        amount = result.get("amount", 0)
        text = f"Счёт на {int(amount)} ₽ создан. Нажмите кнопку ниже, чтобы перейти к оплате."
        keyboard = InlineKeyboardMarkup(
            inline_keyboard=[
                [InlineKeyboardButton(text="Перейти к оплате", url=pay_url)],
                [InlineKeyboardButton(text="◀️ В меню", callback_data="main_menu")],
            ]
        )
        await message.answer(text, reply_markup=keyboard)


def register_text_handlers(dp: Dispatcher) -> None:
    """Register unified text handler."""
    dp.message.register(handle_text_message, F.text)
