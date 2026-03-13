"""Payments module service."""
import logging
from sqlalchemy.ext.asyncio import AsyncSession
from typing import Optional, List
from uuid import UUID
from datetime import datetime, timedelta
import uuid

from .repository import PaymentRepository
from ..users.repository import UserRepository
from ..telegram.service import TelegramService
from ..telegram.bot_service import TelegramBotService
from ..system_settings.service import SystemSettingService

logger = logging.getLogger(__name__)
from .schemas import PaymentCreate, PaymentResponse, PaymentWebhook
from .models import Payment, PaymentStatus
from ..subscriptions.repository import SubscriptionRepository
from ..subscriptions.service import SubscriptionService
from ..subscriptions.models import SubscriptionStatus
from ..subscriptions.repository import SubscriptionPlanRepository
from .providers.yookassa import YooKassaProvider


class PaymentService:
    """Service for payment operations."""

    def __init__(self, db: AsyncSession):
        self.repository = PaymentRepository(db)
        self.db = db
        self.provider = YooKassaProvider()

    async def create_payment(
        self, user_id: str, payment_data: PaymentCreate
    ) -> PaymentResponse:
        """
        Create payment.
        
        Args:
            user_id: User ID
            payment_data: Payment creation data
            
        Returns:
            Payment response with payment URL
        """
        from uuid import UUID

        logger.info("[PAYMENT] create_payment started user_id=%s plan_id=%s return_url=%s", user_id, payment_data.plan_id, payment_data.return_url or "(empty)")

        # Get plan
        plan_repository = SubscriptionPlanRepository(self.db)
        plan_id = UUID(payment_data.plan_id)
        plan = await plan_repository.get_by_id(plan_id)
        if not plan:
            logger.warning("[PAYMENT] Plan not found plan_id=%s", payment_data.plan_id)
            raise ValueError("Plan not found")

        # Calculate amount (use first_month_price if available, else price)
        amount = float(plan.first_month_price or plan.price)
        
        # Get currency from plan or use default
        currency = payment_data.currency
        if not currency and hasattr(plan, 'currency') and plan.currency:
            currency = plan.currency
        if not currency:
            currency = "RUB"
        
        logger.info("[PAYMENT] Plan found name=%s amount=%.2f currency=%s", plan.name, amount, currency)

        # Create payment record
        payment = await self.repository.create({
            "user_id": UUID(user_id),
            "plan_id": plan_id,
            "amount": amount,
            "currency": currency,
            "status": PaymentStatus.PENDING,
            "provider": "yookassa",
            "metadata": {"plan_id": str(plan_id)},
        })
        logger.info("[PAYMENT] DB record created payment_id=%s status=pending", str(payment.id))

        # Create payment with provider
        try:
            provider = self.provider
            provider_result = await provider.create_payment(
                amount=amount,
                currency=payment.currency,
                description=f"Subscription: {plan.name}",
                return_url=f"{payment_data.return_url}?payment_id={payment.id}",
                metadata={
                    "payment_id": str(payment.id),
                    "user_id": user_id,
                    "plan_id": payment_data.plan_id,
                    "idempotence_key": str(uuid.uuid4()),
                },
            )
            pay_url = provider_result.get("payment_url", "")
            logger.info(
                "[PAYMENT] Provider success payment_id=%s provider_payment_id=%s payment_url=%s",
                str(payment.id), provider_result.get("payment_id"), pay_url[:100] + "..." if len(pay_url) > 100 else pay_url
            )

            # Update payment with provider data
            await self.repository.update(
                payment.id,
                {
                    "provider_payment_id": provider_result["payment_id"],
                    "payment_url": provider_result["payment_url"],
                },
            )
            
            await self.db.refresh(payment)
            logger.info("[PAYMENT] create_payment completed payment_id=%s user_id=%s amount=%.2f", str(payment.id), user_id, amount)
            return PaymentResponse.model_validate(payment)

        except Exception as e:
            logger.error(
                "[PAYMENT] create_payment FAILED payment_id=%s user_id=%s error=%s",
                str(payment.id), user_id, str(e), exc_info=True
            )
            # Mark payment as failed
            await self.repository.update(
                payment.id,
                {"status": PaymentStatus.FAILED},
            )
            raise

    async def sync_payment_status_from_provider(self, payment: Payment) -> bool:
        """
        Fetch payment status from YooKassa and update DB.
        Returns True if status was updated.
        """
        if not payment.provider_payment_id:
            logger.warning("[PAYMENT] sync skipped: no provider_payment_id payment_id=%s", str(payment.id))
            return False
        try:
            status = await self.provider.get_payment_status(payment.provider_payment_id)
            if not status:
                logger.info("[PAYMENT] sync no status from provider payment_id=%s provider_id=%s", str(payment.id), payment.provider_payment_id)
                return False
        except Exception as e:
            logger.error("[PAYMENT] sync FAILED payment_id=%s provider_id=%s error=%s", str(payment.id), payment.provider_payment_id, str(e))
            return False

        if status == "succeeded":
            await self.repository.update(payment.id, {"status": PaymentStatus.COMPLETED, "paid_at": datetime.utcnow()})
            await self.db.refresh(payment)
            await self._activate_subscription_from_payment(payment)
            await self._send_payment_success_notification(payment)
            logger.info("[PAYMENT] sync SUCCESS payment_id=%s status=completed subscription activated", str(payment.id))
            return True
        if status == "canceled":
            await self.repository.update(payment.id, {"status": PaymentStatus.FAILED})
            logger.info("[PAYMENT] sync CANCELED payment_id=%s status=failed", str(payment.id))
            return True
        logger.info("[PAYMENT] sync no change payment_id=%s provider_status=%s", str(payment.id), status)
        return False

    async def sync_all_pending_from_provider(self) -> dict:
        """
        Sync all pending payments with provider_payment_id from YooKassa.
        Returns {updated: N, total: M, errors: [...]}.
        """
        pending = await self.repository.get_pending_with_provider_id()
        updated = 0
        errors = []
        for p in pending:
            try:
                if await self.sync_payment_status_from_provider(p):
                    updated += 1
            except Exception as e:
                errors.append({"payment_id": str(p.id), "error": str(e)})
        return {"updated": updated, "total": len(pending), "errors": errors}

    async def get_payment(self, payment_id: str) -> Optional[PaymentResponse]:
        """Get payment by ID."""
        payment = await self.repository.get_by_id(UUID(payment_id))
        if payment:
            return PaymentResponse.model_validate(payment)
        return None

    async def process_webhook(self, webhook_data: PaymentWebhook) -> None:
        """
        Process payment webhook.
        
        Args:
            webhook_data: Webhook data from provider
            
        Raises:
            ValueError: If webhook validation fails
        """
        provider_payment_id = webhook_data.object.get("id", "?")
        logger.info("[PAYMENT] webhook received provider_id=%s event=%s status=%s", provider_payment_id, webhook_data.event, webhook_data.object.get("status"))

        try:
            # Verify webhook signature (if signature provided)
            if webhook_data.signature:
                provider = self.provider
                if not await provider.verify_webhook(
                    webhook_data.object, webhook_data.signature
                ):
                    logger.warning("[PAYMENT] webhook INVALID signature provider_id=%s", provider_payment_id)
                    raise ValueError("Invalid webhook signature")
            else:
                logger.warning("[PAYMENT] webhook without signature (security risk) provider_id=%s", provider_payment_id)

            # Get payment by provider_payment_id
            if not webhook_data.object.get("id"):
                logger.error("[PAYMENT] webhook missing payment ID in object")
                raise ValueError("Missing payment ID in webhook")
            
            payment = await self.repository.get_by_provider_payment_id(
                provider_payment_id
            )
            if not payment:
                logger.error("[PAYMENT] webhook payment NOT FOUND provider_id=%s", provider_payment_id)
                raise ValueError("Payment not found")
            
            # Check if already processed (idempotency)
            if payment.status == PaymentStatus.COMPLETED:
                logger.info("[PAYMENT] webhook idempotency skip payment_id=%s already completed", str(payment.id))
                return  # Already processed
            
            # Update payment status
            webhook_status = webhook_data.object.get("status")
            if webhook_status == "succeeded":
                await self.repository.update(
                    payment.id,
                    {
                        "status": PaymentStatus.COMPLETED,
                        "paid_at": datetime.utcnow(),
                    },
                )
                
                # Activate subscription
                await self._activate_subscription_from_payment(payment)
                await self._send_payment_success_notification(payment)
                logger.info("[PAYMENT] webhook SUCCESS payment_id=%s subscription activated", str(payment.id))
            elif webhook_status == "canceled":
                await self.repository.update(
                    payment.id,
                    {"status": PaymentStatus.FAILED},
                )
                logger.info("[PAYMENT] webhook CANCELED payment_id=%s", str(payment.id))
            else:
                logger.warning("[PAYMENT] webhook unknown status=%s payment_id=%s provider_id=%s", webhook_status, str(payment.id), provider_payment_id)
        except ValueError as ve:
            logger.error("[PAYMENT] webhook validation error: %s provider_id=%s", str(ve), provider_payment_id)
            raise
        except Exception as e:
            logger.error("[PAYMENT] webhook FAILED provider_id=%s error=%s", provider_payment_id, str(e), exc_info=True)
            raise

    async def _activate_subscription_from_payment(self, payment: Payment) -> None:
        """Activate subscription from completed payment."""
        logger.info("[PAYMENT] _activate_subscription payment_id=%s user_id=%s", str(payment.id), str(payment.user_id))

        if not payment.plan_id:
            logger.error(f"Payment {payment.id} has no plan_id")
            return
        
        try:
            # Check if subscription already exists
            subscription_repository = SubscriptionRepository(self.db)
            existing = await subscription_repository.get_active_by_user_id(payment.user_id)
            
            plan_repository = SubscriptionPlanRepository(self.db)
            plan = await plan_repository.get_by_id(payment.plan_id)
            if not plan:
                logger.error(f"Plan {payment.plan_id} not found")
                return
            
            if existing:
                # Extend existing subscription
                if existing.end_date:
                    new_end_date = existing.end_date + timedelta(days=plan.duration_days)
                else:
                    new_end_date = datetime.utcnow() + timedelta(days=plan.duration_days)
                
                await subscription_repository.update(
                    existing.id,
                    {
                        "end_date": new_end_date,
                        "payment_id": payment.id,
                    },
                )
                
                # Link payment to subscription
                await self.repository.update(
                    payment.id,
                    {"subscription_id": existing.id},
                )
                logger.info(f"Extended subscription {existing.id} for payment {payment.id}")
            else:
                # Create new subscription
                start_date = datetime.utcnow()
                end_date = start_date + timedelta(days=plan.duration_days)
                
                subscription = await subscription_repository.create({
                    "user_id": payment.user_id,
                    "plan_id": payment.plan_id,
                    "payment_id": payment.id,
                    "status": SubscriptionStatus.PENDING,
                    "start_date": start_date,
                    "end_date": end_date,
                })
                
                # Activate subscription
                subscription_service = SubscriptionService(self.db)
                await subscription_service.activate_subscription(subscription.id)
                
                # Link payment to subscription
                await self.repository.update(
                    payment.id,
                    {"subscription_id": subscription.id},
                )
                logger.info("[PAYMENT] Created subscription sub_id=%s payment_id=%s", str(subscription.id), str(payment.id))
        except Exception as e:
            logger.error(f"Error activating subscription from payment {payment.id}: {e}", exc_info=True)
            raise

    async def _send_payment_success_notification(self, payment: Payment) -> None:
        """
        After successful payment: generate invite link, format message from settings,
        send to user via Telegram bot. User must have telegram_id.
        """
        user_repo = UserRepository(self.db)
        user = await user_repo.get_by_id(payment.user_id)
        if not user or not user.telegram_id:
            logger.info("[PAYMENT] skip notification: user has no telegram_id user_id=%s", str(payment.user_id))
            return
        try:
            tg_service = TelegramService(self.db)
            invite_resp = await tg_service.generate_invite_link(str(payment.user_id))
            if not invite_resp or not invite_resp.invite_link:
                logger.warning("[PAYMENT] failed to generate invite link user_id=%s", str(payment.user_id))
                return
            settings_svc = SystemSettingService(self.db)
            template = await settings_svc.get("MSG_PAYMENT_SUCCESS")
            if not template:
                template = (
                    "Добрый день, спасибо за оплату.\n"
                    "Ваша подписка активна до {{end_date}}.\n"
                    "Вот ссылка на доступ в закрытый Telegram-канал:\n{{link}}"
                )
            sub_repo = SubscriptionRepository(self.db)
            sub = await sub_repo.get_active_by_user_id(payment.user_id)
            end_date_str = sub.end_date.strftime("%d.%m.%Y") if sub and sub.end_date else "—"
            text = template.replace("{{link}}", invite_resp.invite_link).replace("{{end_date}}", end_date_str)
            bot_svc = await TelegramBotService.create(self.db)
            await bot_svc.send_message(int(user.telegram_id), text)
            await bot_svc.close()
            logger.info("[PAYMENT] notification sent user_id=%s telegram_id=%s", str(payment.user_id), user.telegram_id)
        except Exception as e:
            logger.error("[PAYMENT] notification FAILED user_id=%s error=%s", str(payment.user_id), str(e), exc_info=True)

    async def backfill_subscriptions_from_completed_payments(self) -> dict:
        """
        Create subscriptions for completed payments that have plan_id but no subscription_id.
        Returns {created: N, errors: [...]}.
        """
        payments = await self.repository.get_completed_without_subscription()
        created = 0
        errors = []
        for payment in payments:
            try:
                await self._activate_subscription_from_payment(payment)
                created += 1
            except Exception as e:
                errors.append({"payment_id": str(payment.id), "error": str(e)})
        return {"created": created, "total": len(payments), "errors": errors}

    async def get_user_payments(
        self, user_id: str, skip: int = 0, limit: int = 100
    ) -> List[PaymentResponse]:
        """Get user's payment history."""
        payments = await self.repository.get_by_user_id(
            UUID(user_id), skip=skip, limit=limit
        )
        return [PaymentResponse.model_validate(p) for p in payments]
