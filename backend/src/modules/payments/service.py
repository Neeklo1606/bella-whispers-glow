"""Payments module service."""
from sqlalchemy.ext.asyncio import AsyncSession
from typing import Optional, List
from uuid import UUID
from datetime import datetime, timedelta
import uuid

from .repository import PaymentRepository
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
        
        # Get plan
        plan_repository = SubscriptionPlanRepository(self.db)
        plan_id = UUID(payment_data.plan_id)
        plan = await plan_repository.get_by_id(plan_id)
        if not plan:
            raise ValueError("Plan not found")
        
        # Calculate amount (use first_month_price if available, else price)
        amount = float(plan.first_month_price or plan.price)
        
        # Get currency from plan or use default
        currency = payment_data.currency
        if not currency and hasattr(plan, 'currency') and plan.currency:
            currency = plan.currency
        if not currency:
            currency = "RUB"
        
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
        
        # Create payment with provider
        try:
            provider = await self._get_provider()
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
            
            # Update payment with provider data
            await self.repository.update(
                payment.id,
                {
                    "provider_payment_id": provider_result["payment_id"],
                    "payment_url": provider_result["payment_url"],
                },
            )
            
            await self.db.refresh(payment)
            return PaymentResponse.model_validate(payment)
        
        except Exception as e:
            import logging
            logger = logging.getLogger(__name__)
            logger.error(f"Failed to create payment: {e}", exc_info=True)
            # Mark payment as failed
            await self.repository.update(
                payment.id,
                {"status": PaymentStatus.FAILED},
            )
            raise

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
        import logging
        logger = logging.getLogger(__name__)
        
        try:
            # Verify webhook signature (if signature provided)
            if webhook_data.signature:
                provider = await self._get_provider()
                if not await provider.verify_webhook(
                    webhook_data.object, webhook_data.signature
                ):
                    logger.warning("Invalid webhook signature")
                    raise ValueError("Invalid webhook signature")
            else:
                logger.warning("Webhook received without signature - security risk in production")
            
            # Get payment by provider_payment_id
            provider_payment_id = webhook_data.object.get("id")
            if not provider_payment_id:
                logger.error("Webhook missing payment ID")
                raise ValueError("Missing payment ID in webhook")
            
            payment = await self.repository.get_by_provider_payment_id(
                provider_payment_id
            )
            if not payment:
                logger.error(f"Payment not found for provider_payment_id: {provider_payment_id}")
                raise ValueError("Payment not found")
            
            # Check if already processed (idempotency)
            if payment.status == PaymentStatus.COMPLETED:
                logger.info(f"Payment {payment.id} already processed - skipping (idempotency)")
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
                logger.info(f"Payment {payment.id} completed and subscription activated")
            elif webhook_status == "canceled":
                await self.repository.update(
                    payment.id,
                    {"status": PaymentStatus.FAILED},
                )
                logger.info(f"Payment {payment.id} was canceled")
            else:
                logger.warning(f"Payment {payment.id} received unknown status: {webhook_status}")
        except ValueError:
            # Re-raise validation errors
            raise
        except Exception as e:
            logger.error(f"Error processing webhook: {e}", exc_info=True)
            raise

    async def _activate_subscription_from_payment(self, payment: Payment) -> None:
        """Activate subscription from completed payment."""
        import logging
        logger = logging.getLogger(__name__)
        
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
                logger.info(f"Created and activated subscription {subscription.id} for payment {payment.id}")
        except Exception as e:
            logger.error(f"Error activating subscription from payment {payment.id}: {e}", exc_info=True)
            raise

    async def get_user_payments(
        self, user_id: str, skip: int = 0, limit: int = 100
    ) -> List[PaymentResponse]:
        """Get user's payment history."""
        payments = await self.repository.get_by_user_id(
            UUID(user_id), skip=skip, limit=limit
        )
        return [PaymentResponse.model_validate(p) for p in payments]
