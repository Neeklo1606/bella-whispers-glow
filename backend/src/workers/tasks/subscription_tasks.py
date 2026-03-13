"""
Subscription-related background tasks.
"""
import logging
from datetime import datetime
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from ...core.db import AsyncSessionLocal
from ...modules.subscriptions.repository import SubscriptionRepository
from ...modules.subscriptions.models import Subscription, SubscriptionStatus
from ...modules.telegram.bot_service import TelegramBotService
from ...modules.channel_logs.service import ChannelAccessLogService
from ...modules.channel_logs.models import ChannelAccessEventType
from ...modules.system_settings.service import SystemSettingService

logger = logging.getLogger(__name__)

REMINDER_DAYS_SETTINGS = {
    7: "MSG_REMINDER_7",
    3: "MSG_REMINDER_3",
    1: "MSG_REMINDER_1",
    0: "MSG_REMINDER_0",
}


async def check_expired_subscriptions():
    """Check and expire subscriptions."""
    async with AsyncSessionLocal() as db:
        try:
            logger.info("Checking expired subscriptions...")
            
            subscription_repository = SubscriptionRepository(db)
            bot_service = await TelegramBotService.create(db)
            log_service = ChannelAccessLogService(db)
            
            # Find subscriptions with end_date < NOW() and status = 'active'
            expired_subscriptions = await subscription_repository.get_expired_subscriptions()
            
            logger.info(f"Found {len(expired_subscriptions)} expired subscriptions")
            
            for subscription in expired_subscriptions:
                try:
                    # Load user relationship
                    from sqlalchemy.orm import selectinload
                    from sqlalchemy import select
                    from ...modules.subscriptions.models import Subscription
                    
                    result = await db.execute(
                        select(Subscription)
                        .options(selectinload(Subscription.user))
                        .where(Subscription.id == subscription.id)
                    )
                    subscription = result.scalar_one()
                    
                    # Update status to 'expired'
                    await subscription_repository.update(
                        subscription.id,
                        {"status": SubscriptionStatus.EXPIRED},
                    )
                    
                    # Log expiration
                    if subscription.user:
                        await log_service.log_event(
                            user_id=subscription.user.id,
                            event_type=ChannelAccessEventType.EXPIRED,
                            telegram_id=subscription.user.telegram_id if subscription.user else None,
                            subscription_id=subscription.id,
                        )
                    
                    # Remove user from Telegram channel
                    if subscription.user and subscription.user.telegram_id:
                        success = await bot_service.remove_chat_member(
                            subscription.user.telegram_id
                        )
                        if success:
                            logger.info(
                                f"Removed user {subscription.user.telegram_id} from channel"
                            )
                            # Log kicked event
                            await log_service.log_event(
                                user_id=subscription.user.id,
                                event_type=ChannelAccessEventType.KICKED,
                                telegram_id=subscription.user.telegram_id,
                                subscription_id=subscription.id,
                            )
                        
                        # Send notification (editable in admin MSG_SUBSCRIPTION_EXPIRED)
                        from ...modules.system_settings.service import SystemSettingService
                        settings_svc = SystemSettingService(db)
                        message = await settings_svc.get("MSG_SUBSCRIPTION_EXPIRED")
                        if not message:
                            message = "Срок вашей подписки закончился. Чтобы снова получить доступ, оформите продление."
                        miniapp_url = await settings_svc.get("MINIAPP_URL") or "https://app.bellahasias.ru"
                        message += f"\n\nПерейти к тарифам: {miniapp_url.rstrip('/')}/pricing"
                        await bot_service.send_message(
                            subscription.user.telegram_id,
                            message,
                        )
                    
                    logger.info(f"Expired subscription {subscription.id}")
                    
                except Exception as e:
                    logger.error(
                        f"Error processing expired subscription {subscription.id}: {e}"
                    )
            
            await bot_service.close()
            logger.info("Finished checking expired subscriptions")
            
        except Exception as e:
            logger.error(f"Error checking expired subscriptions: {e}")


async def process_auto_renewals():
    """Process automatic subscription renewals."""
    async with AsyncSessionLocal() as db:
        try:
            # TODO: Implement auto-renewal logic
            # 1. Find subscriptions with auto_renew = true and next_billing_date = TODAY
            # 2. Create payment
            # 3. Process payment
            # 4. Extend subscription if payment successful
            logger.info("Processing auto-renewals...")
        except Exception as e:
            logger.error(f"Error processing auto-renewals: {e}")


async def send_renewal_reminders():
    """Send renewal reminders: 7, 3, 1, 0 days before end. Uses MSG_REMINDER_* settings."""
    async with AsyncSessionLocal() as db:
        try:
            sub_repo = SubscriptionRepository(db)
            settings_svc = SystemSettingService(db)
            miniapp_url = await settings_svc.get("MINIAPP_URL") or "https://app.bellahasias.ru"
            bot_svc = await TelegramBotService.create(db)
            sent = 0
            for days, key in REMINDER_DAYS_SETTINGS.items():
                subs = await sub_repo.get_subscriptions_expiring_in_days(days)
                template = await settings_svc.get(key)
                if not template:
                    template = f"Добрый день. Ваша подписка заканчивается через {days} дн."
                suffix = f"\n\nПродлить подписку: {miniapp_url.rstrip('/')}/pricing"
                for sub in subs:
                    result = await db.execute(
                        select(Subscription).options(selectinload(Subscription.user)).where(Subscription.id == sub.id)
                    )
                    sub = result.scalar_one()
                    if not sub.user or not sub.user.telegram_id:
                        continue
                    end_str = sub.end_date.strftime("%d.%m.%Y") if sub.end_date else "—"
                    text = template.replace("{{end_date}}", end_str) + suffix
                    try:
                        ok = await bot_svc.send_message(int(sub.user.telegram_id), text)
                        if ok:
                            sent += 1
                    except Exception as e:
                        logger.warning("Reminder send failed user=%s: %s", sub.user.telegram_id, e)
            await bot_svc.close()
            if sent:
                logger.info("Sent %d renewal reminders", sent)
        except Exception as e:
            logger.error("Error sending renewal reminders: %s", e)
