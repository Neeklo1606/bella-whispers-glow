"""
Bot API endpoints: subscription by telegram_id, create payment.
Secured with X-Bot-Secret.
"""
from fastapi import APIRouter, Depends, HTTPException, Query
from pydantic import BaseModel
from sqlalchemy.ext.asyncio import AsyncSession
from uuid import UUID

from ...core.db import get_db
from ...core.security.bot_auth import verify_bot_secret
from ..users.repository import UserRepository
from ..subscriptions.repository import SubscriptionRepository, SubscriptionPlanRepository
from ..subscriptions.models import SubscriptionStatus
from ..payments.service import PaymentService
from ..system_settings.service import SystemSettingService

router = APIRouter()


class RegisterUserRequest(BaseModel):
    """Register or update bot user in DB."""
    telegram_id: int
    username: str = ""
    first_name: str = ""
    last_name: str = ""


@router.post("/register-user")
async def register_bot_user(
    data: RegisterUserRequest,
    _: str = Depends(verify_bot_secret),
    db: AsyncSession = Depends(get_db),
):
    """Save bot user to DB (get or create). Called when user interacts with bot."""
    from ..users.enums import UserRole

    user_repo = UserRepository(db)
    user = await user_repo.get_by_telegram_id(data.telegram_id)
    if user:
        await user_repo.update(user.id, {
            "username": data.username or None,
            "first_name": data.first_name or None,
            "last_name": data.last_name or None,
        })
        await db.refresh(user)
        return {"user_id": str(user.id), "created": False}
    user = await user_repo.create({
        "telegram_id": data.telegram_id,
        "username": data.username or None,
        "first_name": data.first_name or None,
        "last_name": data.last_name or None,
        "role": UserRole.USER,
    })
    await db.flush()
    return {"user_id": str(user.id), "created": True}


class CreatePaymentRequest(BaseModel):
    """Request to create payment from bot."""
    telegram_id: int
    plan_id: str
    email: str
    first_name: str = ""
    last_name: str = ""
    username: str = ""


@router.get("/subscription")
async def get_subscription_by_telegram(
    telegram_id: int = Query(..., description="Telegram user ID"),
    _: str = Depends(verify_bot_secret),
    db: AsyncSession = Depends(get_db),
):
    """
    Get user subscription by Telegram ID.
    Returns subscription info or null if no active subscription.
    """
    user_repo = UserRepository(db)
    sub_repo = SubscriptionRepository(db)
    user = await user_repo.get_by_telegram_id(telegram_id)
    if not user:
        return {"subscription": None}
    subscription = await sub_repo.get_active_by_user_id(user.id)
    if not subscription:
        return {"subscription": None}
    return {
        "subscription": {
            "id": str(subscription.id),
            "status": subscription.status.value,
            "end_date": subscription.end_date.isoformat() if subscription.end_date else None,
        },
    }


@router.post("/create-payment")
async def create_payment_from_bot(
    data: CreatePaymentRequest,
    _: str = Depends(verify_bot_secret),
    db: AsyncSession = Depends(get_db),
):
    """
    Create payment for user identified by telegram_id.
    Creates user if not exists. Returns payment_url for YooKassa.
    """
    user_repo = UserRepository(db)
    plan_repo = SubscriptionPlanRepository(db)
    settings_svc = SystemSettingService(db)

    plan = await plan_repo.get_by_id(UUID(data.plan_id))
    if not plan or not plan.is_active:
        raise HTTPException(status_code=404, detail="Plan not found")

    email = (data.email or "").strip()
    if not email:
        raise HTTPException(status_code=400, detail="Email is required")

    user = await user_repo.get_by_telegram_id(data.telegram_id)
    if not user:
        from ..users.enums import UserRole
        user = await user_repo.create({
            "telegram_id": data.telegram_id,
            "username": data.username or None,
            "first_name": data.first_name or None,
            "last_name": data.last_name or None,
            "email": email,
            "role": UserRole.USER,
        })
        await db.flush()
    elif user.email != email:
        await user_repo.update(user.id, {"email": email})
        await db.refresh(user)

    miniapp_url = await settings_svc.get("MINIAPP_URL") or "https://app.bellahasias.ru"
    return_url = f"{miniapp_url.rstrip('/')}/pricing?paid=1"

    payment_svc = PaymentService(db)
    from ..payments.schemas import PaymentCreate

    payment_data = PaymentCreate(
        plan_id=data.plan_id,
        currency="RUB",
        return_url=return_url,
    )
    payment = await payment_svc.create_payment(str(user.id), payment_data)
    return {
        "payment_id": payment.id,
        "payment_url": payment.payment_url,
        "amount": payment.amount,
    }
