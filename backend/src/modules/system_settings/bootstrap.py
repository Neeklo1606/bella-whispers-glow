"""
Bootstrap default system settings and subscription plan on startup.
"""
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from .service import SystemSettingService

DEFAULT_SETTINGS = {
    "TELEGRAM_BOT_TOKEN": "8716981874:AAE2hzfIx8Gk0syIGwmp0ZzP36TRO9CtR8g",
    "TELEGRAM_CHANNEL_ID": "-1003802293810",
    "SUPPORT_USERNAME": "@bellahasias_bot",
    "MINIAPP_URL": "https://app.bellahasias.ru",
    "OFFER_URL": "https://bellahasias.ru/privacy",
    "TELEGRAM_BOT_LINK": "https://t.me/bellahasias_bot",
    "CONTACT_LINK": "https://t.me/Bella_hasias",
    "PRICE_NOTE": "далее 1500 ₽/мес · отмена в любой момент",
    "FEATURES": '["Ежемесячные капсулы","Разборы трендов","Персональные рекомендации","Промокоды и находки"]',
    "FAQ_ITEMS": '[{"q":"Я ничего не понимаю в стиле. Мне подойдёт?","a":"Конечно! В чате есть разделы: inspo, тренды, капсулы и живые обзоры."},{"q":"Зачем мне этот чат?","a":"Первый опыт работы со стилистом."},{"q":"Успею ли я?","a":"Материалы доступны в записи, смотрите в своём темпе."},{"q":"Что если не продлю?","a":"Доступ закроется. Вернуться можно в любой момент."},{"q":"Можно войти с середины месяца?","a":"Да, подписка 30 дней с момента оплаты."},{"q":"Материалы навсегда?","a":"Доступ активен пока действует подписка."}]',
    "PLAN_TITLE": "Подписка на месяц",
    "PRICE_AFTER": "1500",
}


async def ensure_default_settings(db: AsyncSession) -> None:
    """
    Ensure default Telegram (and related) settings exist in system_settings.
    Creates a record for each key only if it does not already exist.
    """
    service = SystemSettingService(db)
    for key, value in DEFAULT_SETTINGS.items():
        existing = await service.get(key)
        if existing is None:
            await service.set(key, value)
    await _ensure_default_plan(db)


async def _ensure_default_plan(db: AsyncSession) -> None:
    """Create default subscription plan (1 месяц, 990 ₽) if none exist."""
    from ..subscriptions.models import SubscriptionPlan
    result = await db.execute(select(SubscriptionPlan).where(SubscriptionPlan.is_active == True))
    if result.scalars().first():
        return
    plan = SubscriptionPlan(
        name="1 месяц",
        description="Доступ в закрытый канал на 30 дней",
        price=990,
        first_month_price=990,
        duration_days=30,
        currency="RUB",
        features=["Доступ к закрытому Telegram каналу"],
        is_active=True,
    )
    db.add(plan)
