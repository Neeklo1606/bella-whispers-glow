"""
Unified text message handler: feedback forward only.
Payment is done strictly in mini app (YooKassa).
"""
import logging
from aiogram import Dispatcher, F
from aiogram.types import Message

from ..keyboards.main_menu import get_main_menu_keyboard
from ..utils.runtime_settings import get as get_runtime
from ..utils.user_state import get_state, pop_state

logger = logging.getLogger(__name__)


async def handle_text_message(message: Message):
    """Route text by user state: awaiting_feedback -> forward."""
    user = message.from_user
    if not user:
        return
    state = get_state(user.id)
    if not state or state.get("state") != "awaiting_feedback":
        return

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


def register_text_handlers(dp: Dispatcher) -> None:
    """Register unified text handler."""
    dp.message.register(handle_text_message, F.text)
