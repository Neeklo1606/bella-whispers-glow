"""
Admin module API routes.
All routes require admin authentication.
"""
from fastapi import APIRouter, Depends, HTTPException, status, Query

from .plans_router import router as plans_router
from .broadcasts_router import router as admin_broadcasts_router
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func
from typing import Dict, List
from datetime import datetime, date, timedelta
from uuid import UUID

from ...core.db import get_db
from ...core.security import require_admin_user
from ...modules.system_settings.service import SystemSettingService
from ...modules.system_settings.schemas import SettingResponse, SettingUpdate
from ...modules.users.models import User
from ...modules.subscriptions.repository import SubscriptionRepository
from ...modules.subscriptions.models import SubscriptionStatus
from ...modules.payments.repository import PaymentRepository
from ...modules.payments.models import PaymentStatus
from ...modules.users.repository import UserRepository

router = APIRouter()

router.include_router(plans_router, prefix="/plans", tags=["admin-plans"])
router.include_router(admin_broadcasts_router, prefix="/broadcasts", tags=["admin-broadcasts"])


@router.get("/dashboard")
async def admin_dashboard(
    admin_user: User = Depends(require_admin_user),
    db: AsyncSession = Depends(get_db),
):
    """
    Admin dashboard with analytics.
    """
    # Import models
    from ...modules.subscriptions.models import Subscription
    from ...modules.payments.models import Payment
    
    # Total users
    total_users_result = await db.execute(
        select(func.count(User.id))
    )
    total_users = total_users_result.scalar() or 0
    
    # Active subscriptions
    active_subs_result = await db.execute(
        select(func.count(Subscription.id)).where(
            Subscription.status == SubscriptionStatus.ACTIVE
        )
    )
    active_subscriptions = active_subs_result.scalar() or 0
    
    # Payments today
    today = date.today()
    payments_today_result = await db.execute(
        select(func.count(Payment.id)).where(
            func.date(Payment.created_at) == today
        )
    )
    payments_today = payments_today_result.scalar() or 0
    
    # Revenue today
    revenue_today_result = await db.execute(
        select(func.sum(Payment.amount)).where(
            func.date(Payment.created_at) == today,
            Payment.status == PaymentStatus.COMPLETED,
        )
    )
    revenue_today = float(revenue_today_result.scalar() or 0)
    
    # Total revenue
    revenue_total_result = await db.execute(
        select(func.sum(Payment.amount)).where(
            Payment.status == PaymentStatus.COMPLETED,
        )
    )
    revenue_total = float(revenue_total_result.scalar() or 0)
    
    # Churn rate: (expired + cancelled) / total ever had subscription
    total_subs_result = await db.execute(select(func.count(Subscription.id)))
    total_subs = total_subs_result.scalar() or 0
    churned_result = await db.execute(
        select(func.count(Subscription.id)).where(
            Subscription.status.in_([SubscriptionStatus.EXPIRED, SubscriptionStatus.CANCELLED])
        )
    )
    churned = churned_result.scalar() or 0
    churn_rate = round((churned / total_subs * 100), 2) if total_subs else 0.0
    
    return {
        "users_count": total_users,
        "active_subscriptions": active_subscriptions,
        "revenue_today": revenue_today,
        "revenue_total": revenue_total,
        "churn_rate": churn_rate,
        "user": {
            "id": str(admin_user.id),
            "email": admin_user.email,
            "role": admin_user.role.value,
        },
    }


@router.get("/subscriptions")
async def admin_get_subscriptions(
    admin_user: User = Depends(require_admin_user),
    db: AsyncSession = Depends(get_db),
    skip: int = 0,
    limit: int = 100,
):
    """Get all subscriptions."""
    subscription_repo = SubscriptionRepository(db)
    from ...modules.subscriptions.models import Subscription
    result = await db.execute(
        select(Subscription)
        .order_by(Subscription.created_at.desc())
        .offset(skip)
        .limit(limit)
    )
    subscriptions = list(result.scalars().all())
    from ...modules.subscriptions.schemas import SubscriptionResponse
    return [SubscriptionResponse.model_validate(s) for s in subscriptions]


@router.get("/payments")
async def admin_get_payments(
    admin_user: User = Depends(require_admin_user),
    db: AsyncSession = Depends(get_db),
    skip: int = 0,
    limit: int = 100,
):
    """Get all payments."""
    from ...modules.payments.models import Payment
    result = await db.execute(
        select(Payment)
        .order_by(Payment.created_at.desc())
        .offset(skip)
        .limit(limit)
    )
    payments = list(result.scalars().all())
    from ...modules.payments.schemas import PaymentResponse
    return [PaymentResponse.model_validate(p) for p in payments]


@router.get("/users")
async def admin_get_users(
    admin_user: User = Depends(require_admin_user),
    db: AsyncSession = Depends(get_db),
    skip: int = 0,
    limit: int = 100,
):
    """Get all users."""
    user_repo = UserRepository(db)
    users = await user_repo.get_all(skip=skip, limit=limit)
    from ...modules.users.schemas import UserResponse
    return [UserResponse.model_validate(u) for u in users]


@router.post("/subscriptions/{subscription_id}/revoke")
async def admin_revoke_subscription(
    subscription_id: str,
    admin_user: User = Depends(require_admin_user),
    db: AsyncSession = Depends(get_db),
):
    """Revoke subscription."""
    subscription_repo = SubscriptionRepository(db)
    subscription = await subscription_repo.get_by_id(UUID(subscription_id))
    if not subscription:
        raise HTTPException(status_code=404, detail="Subscription not found")
    
    await subscription_repo.update(
        subscription.id,
        {"status": SubscriptionStatus.CANCELLED, "cancelled_at": datetime.utcnow()},
    )
    
    # Remove user from channel
    if subscription.user and subscription.user.telegram_id:
        from ...modules.telegram.bot_service import TelegramBotService
        bot_service = await TelegramBotService.create(db)
        await bot_service.remove_chat_member(subscription.user.telegram_id)
        await bot_service.close()
    
    from ...modules.subscriptions.schemas import SubscriptionResponse
    await db.refresh(subscription)
    return SubscriptionResponse.model_validate(subscription)


@router.post("/subscriptions/{subscription_id}/extend")
async def admin_extend_subscription(
    subscription_id: str,
    days: int,
    admin_user: User = Depends(require_admin_user),
    db: AsyncSession = Depends(get_db),
):
    """Extend subscription."""
    subscription_repo = SubscriptionRepository(db)
    subscription = await subscription_repo.get_by_id(UUID(subscription_id))
    if not subscription:
        raise HTTPException(status_code=404, detail="Subscription not found")
    
    if subscription.end_date:
        new_end_date = subscription.end_date + timedelta(days=days)
    else:
        new_end_date = datetime.utcnow() + timedelta(days=days)
    
    await subscription_repo.update(
        subscription.id,
        {"end_date": new_end_date},
    )
    
    from ...modules.subscriptions.schemas import SubscriptionResponse
    await db.refresh(subscription)
    return SubscriptionResponse.model_validate(subscription)


@router.post("/users/{user_id}/ban")
async def admin_ban_user(
    user_id: str,
    admin_user: User = Depends(require_admin_user),
    db: AsyncSession = Depends(get_db),
):
    """Ban user."""
    user_repo = UserRepository(db)
    user = await user_repo.get_by_id(UUID(user_id))
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    
    # Cancel all active subscriptions
    subscription_repo = SubscriptionRepository(db)
    subscription = await subscription_repo.get_active_by_user_id(user.id)
    if subscription:
        await subscription_repo.update(
            subscription.id,
            {"status": SubscriptionStatus.CANCELLED, "cancelled_at": datetime.utcnow()},
        )
        
        # Remove from channel
        if user.telegram_id:
            from ...modules.telegram.bot_service import TelegramBotService
            bot_service = await TelegramBotService.create(db)
            await bot_service.remove_chat_member(user.telegram_id)
            await bot_service.close()
    
    from ...modules.users.schemas import UserResponse
    return {"success": True, "message": "User banned"}


@router.get("/users/{user_id}/subscriptions")
async def admin_get_user_subscriptions(
    user_id: str,
    admin_user: User = Depends(require_admin_user),
    db: AsyncSession = Depends(get_db),
):
    """Get subscriptions for a user."""
    subscription_repo = SubscriptionRepository(db)
    subscriptions = await subscription_repo.get_all_by_user_id(UUID(user_id))
    from ...modules.subscriptions.schemas import SubscriptionResponse
    return [SubscriptionResponse.model_validate(s) for s in subscriptions]


_DEFAULT_BOT_TOKEN = "8716981874:AAE2hzfIx8Gk0syIGwmp0ZzP36TRO9CtR8g"
_DEFAULT_CHANNEL_ID = "-1003802293810"


@router.post("/test/telegram")
async def admin_test_telegram(
    admin_user: User = Depends(require_admin_user),
    db: AsyncSession = Depends(get_db),
):
    """Test Telegram bot token and channel access. Uses defaults if not set."""
    service = SystemSettingService(db)
    settings = await service.get_settings()
    s_token = settings.get("TELEGRAM_BOT_TOKEN")
    token_val = str(s_token.value).strip() if s_token and s_token.value else ""
    if not token_val:
        token_val = _DEFAULT_BOT_TOKEN
    s_channel = settings.get("TELEGRAM_CHANNEL_ID")
    channel_val = str(s_channel.value).strip() if s_channel and s_channel.value else ""
    if not channel_val:
        channel_val = _DEFAULT_CHANNEL_ID
    
    import httpx
    try:
        async with httpx.AsyncClient() as client:
            r = await client.get(f"https://api.telegram.org/bot{token_val}/getMe", timeout=10)
            data = r.json()
            if not data.get("ok"):
                return {"ok": False, "error": data.get("description", "Invalid bot token")}
        
        if channel_val:
            async with httpx.AsyncClient() as client:
                r2 = await client.get(
                    f"https://api.telegram.org/bot{token_val}/getChat?chat_id={channel_val}",
                    timeout=10
                )
                data2 = r2.json()
                if not data2.get("ok"):
                    return {"ok": True, "bot": data.get("result"), "channel": None, "channel_error": data2.get("description", "Channel access failed")}
                return {"ok": True, "bot": data.get("result"), "channel": data2.get("result")}
        
        return {"ok": True, "bot": data.get("result"), "channel": None}
    except Exception as e:
        return {"ok": False, "error": str(e)}


@router.post("/test/payment")
async def admin_test_payment(
    admin_user: User = Depends(require_admin_user),
    db: AsyncSession = Depends(get_db),
):
    """Test YooKassa payment configuration."""
    service = SystemSettingService(db)
    settings = await service.get_settings()
    
    def get_val(key: str) -> str:
        s = settings.get(key)
        if s and s.value is not None:
            return str(s.value)
        return ""
    
    shop_id = get_val("YOOKASSA_SHOP_ID")
    secret = get_val("YOOKASSA_SECRET_KEY")
    
    if not shop_id or not secret:
        return {"ok": False, "error": "YOOKASSA_SHOP_ID or YOOKASSA_SECRET_KEY is not set"}
    
    import httpx
    import base64
    try:
        auth = base64.b64encode(f"{shop_id}:{secret}".encode()).decode()
        async with httpx.AsyncClient() as client:
            r = await client.post(
                "https://api.yookassa.ru/v3/payments",
                headers={"Authorization": f"Basic {auth}", "Idempotence-Key": str(UUID())},
                json={"amount": {"value": "1.00", "currency": "RUB"}, "capture": True, "description": "Admin test"},
                timeout=10
            )
            if r.status_code in (200, 201):
                return {"ok": True, "message": "YooKassa configured and reachable"}
            return {"ok": False, "error": r.text or f"HTTP {r.status_code}"}
    except Exception as e:
        return {"ok": False, "error": str(e)}


@router.get("/settings", response_model=Dict[str, SettingResponse])
async def admin_get_settings(
    admin_user: User = Depends(require_admin_user),
    db: AsyncSession = Depends(get_db),
):
    """Get all system settings."""
    service = SystemSettingService(db)
    return await service.get_settings()


# Critical security settings that cannot be modified at runtime
_PROTECTED_SETTINGS = frozenset({"SECRET_KEY"})


@router.put("/settings/{key}", response_model=SettingResponse)
async def admin_update_setting(
    key: str,
    setting_data: SettingUpdate,
    admin_user: User = Depends(require_admin_user),
    db: AsyncSession = Depends(get_db),
):
    """Update system setting by key."""
    if key in _PROTECTED_SETTINGS:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="This setting cannot be modified at runtime. Change environment variables and restart the server.",
        )
    service = SystemSettingService(db)
    return await service.update_setting(key, setting_data)
