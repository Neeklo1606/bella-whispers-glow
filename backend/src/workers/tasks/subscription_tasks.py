"""
Subscription-related background tasks.
"""
import logging
from datetime import datetime
from sqlalchemy.ext.asyncio import AsyncSession

from ...core.db import AsyncSessionLocal
from ...modules.subscriptions.repository import SubscriptionRepository
from ...modules.subscriptions.models import SubscriptionStatus
from ...modules.telegram.bot_service import TelegramBotService
from ...modules.channel_logs.service import ChannelAccessLogService
from ...modules.channel_logs.models import ChannelAccessEventType

logger = logging.getLogger(__name__)


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
                        
                        # Send notification
                        message = (
                            "❌ Ваша подписка истекла.\n\n"
                            "Доступ к каналу был отозван.\n"
                            "Для продления подписки используйте Mini App."
                        )
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
    """Send renewal reminders to users."""
    async with AsyncSessionLocal() as db:
        try:
            # TODO: Implement renewal reminders
            # 1. Find subscriptions expiring in 3 days with auto_renew = false
            # 2. Send reminder via Telegram bot
            logger.info("Sending renewal reminders...")
        except Exception as e:
            logger.error(f"Error sending renewal reminders: {e}")
