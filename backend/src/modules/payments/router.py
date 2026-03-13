"""Payments module API routes."""
import logging
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from typing import List

from ...core.db import get_db

logger = logging.getLogger(__name__)
from ...core.security import get_current_user_id
from .service import PaymentService
from .schemas import PaymentCreate, PaymentResponse, PaymentWebhook

router = APIRouter()


@router.post("/create", response_model=PaymentResponse)
async def create_payment(
    payment_data: PaymentCreate,
    user_id: str = Depends(get_current_user_id),
    db: AsyncSession = Depends(get_db),
):
    """Create payment."""
    logger.info("[PAYMENT] API create_payment user_id=%s plan_id=%s", user_id, payment_data.plan_id)
    service = PaymentService(db)
    result = await service.create_payment(user_id, payment_data)
    logger.info("[PAYMENT] API create_payment OK payment_id=%s", result.id)
    return result


@router.get("/{payment_id}", response_model=PaymentResponse)
async def get_payment(
    payment_id: str,
    user_id: str = Depends(get_current_user_id),
    db: AsyncSession = Depends(get_db),
):
    """Get payment by ID."""
    service = PaymentService(db)
    payment = await service.get_payment(payment_id)
    if not payment:
        raise HTTPException(status_code=404, detail="Payment not found")
    return payment


@router.get("/history", response_model=List[PaymentResponse])
async def get_payment_history(
    user_id: str = Depends(get_current_user_id),
    db: AsyncSession = Depends(get_db),
):
    """Get payment history."""
    service = PaymentService(db)
    return await service.get_user_payments(user_id)


@router.post("/webhook")
async def payment_webhook(
    webhook_data: PaymentWebhook,
    db: AsyncSession = Depends(get_db),
):
    """Process payment webhook from provider."""
    provider_id = webhook_data.object.get("id", "?") if webhook_data.object else "?"
    logger.info("[PAYMENT] API webhook event=%s provider_id=%s status=%s", webhook_data.event, provider_id, webhook_data.object.get("status") if webhook_data.object else "?")

    try:
        service = PaymentService(db)
        await service.process_webhook(webhook_data)
        logger.info(f"Webhook processed successfully: {webhook_data.object.get('id', 'unknown')}")
        return {"status": "ok"}
    except ValueError as e:
        logger.error(f"Webhook validation error: {e}")
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        logger.error("[PAYMENT] API webhook error provider_id=%s error=%s", provider_id, str(e), exc_info=True)
        raise HTTPException(status_code=500, detail="Internal server error")
