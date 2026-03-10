"""
Payment handlers: Оплата российской картой flow (callback only; text in text_messages).
"""
from aiogram import Dispatcher, F
from aiogram.types import CallbackQuery

from ..utils.user_state import set_state


async def start_card_payment(callback: CallbackQuery):
    """User clicked 'Оплата российской картой' - ask for email."""
    await callback.answer()
    if not callback.data or ":" not in callback.data:
        return
    _, plan_id = callback.data.split(":", 1)
    user = callback.from_user
    if not user:
        return
    set_state(user.id, "awaiting_email", plan_id=plan_id)
    text = "Введите вашу электронную почту."
    try:
        await callback.message.edit_text(text, reply_markup=None)
    except Exception:
        await callback.message.answer(text)


def register_payment_handlers(dp: Dispatcher) -> None:
    """Register payment handlers."""
    dp.callback_query.register(start_card_payment, F.data.startswith("pay_card:"))
