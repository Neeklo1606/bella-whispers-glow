"""Payments module API routes."""
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from typing import List

from ...core.db import get_db
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
    service = PaymentService(db)
    return await service.create_payment(user_id, payment_data)


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
    import logging
    logger = logging.getLogger(__name__)
    
    try:
        service = PaymentService(db)
        await service.process_webhook(webhook_data)
        logger.info(f"Webhook processed successfully: {webhook_data.object.get('id', 'unknown')}")
        return {"status": "ok"}
    except ValueError as e:
        logger.error(f"Webhook validation error: {e}")
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        logger.error(f"Webhook processing error: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail="Internal server error")
