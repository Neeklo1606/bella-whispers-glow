"""
MiniApp content API. Returns all content for MiniApp (no auth).
"""
import json
from typing import Any
from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from ...core.db import get_db
from ..system_settings.service import SystemSettingService
from ..subscriptions.service import SubscriptionService

router = APIRouter()

CONTENT_KEYS = [
    "MINIAPP_URL", "OFFER_URL", "SUPPORT_USERNAME",
    "TELEGRAM_BOT_LINK", "CONTACT_LINK", "PRICE_NOTE", "PRICE_AFTER",
    "FEATURES", "FAQ_ITEMS", "PLAN_TITLE",
]


def _parse_json(val: Any) -> Any:
    if val is None:
        return None
    if isinstance(val, (list, dict)):
        return val
    s = str(val).strip()
    if not s:
        return None
    try:
        return json.loads(s)
    except (json.JSONDecodeError, TypeError):
        return s


@router.get("/content")
async def get_miniapp_content(db: AsyncSession = Depends(get_db)):
    """Return all content for MiniApp: plans + content settings."""
    settings_svc = SystemSettingService(db)
    plans_svc = SubscriptionService(db)
    plans = await plans_svc.get_plans()
    content: dict[str, Any] = {
        "plans": [p.model_dump() for p in plans],
    }
    for key in CONTENT_KEYS:
        val = await settings_svc.get(key)
        if val is not None and val != "":
            if key in ("FEATURES", "FAQ_ITEMS"):
                content[key.lower()] = _parse_json(val)
            else:
                content[key.lower()] = str(val)
    # Defaults for missing
    content.setdefault("telegram_bot_link", "https://t.me/bellahasias_bot")
    content.setdefault("contact_link", "https://t.me/Bella_hasias")
    content.setdefault("offer_url", "https://bellahasias.ru/privacy")
    content.setdefault("miniapp_url", "https://app.bellahasias.ru")
    content.setdefault("support_username", "bellahasias_bot")
    content.setdefault("price_note", "далее 1500 ₽/мес · отмена в любой момент")
    content.setdefault("price_after", "1500")
    content.setdefault("plan_title", "Подписка на месяц")
    content.setdefault("features", [
        "Ежемесячные капсулы", "Разборы трендов",
        "Персональные рекомендации", "Промокоды и находки"
    ])
    content.setdefault("faq_items", [
        {"q": "Я ничего не понимаю в стиле. Мне подойдёт?", "a": "Конечно! В чате есть разделы: inspo, тренды, капсулы."},
        {"q": "Зачем мне этот чат?", "a": "Первый опыт работы со стилистом."},
    ])
    return content
