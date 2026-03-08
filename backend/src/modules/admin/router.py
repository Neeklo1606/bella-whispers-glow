"""
Admin module API routes.
All routes require admin authentication.
"""
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func
from typing import Dict, List
from datetime import datetime, date
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
    
    return {
        "metrics": {
            "total_users": total_users,
            "active_subscriptions": active_subscriptions,
            "payments_today": payments_today,
            "revenue_today": revenue_today,
            "revenue_total": revenue_total,
        },
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


@router.get("/settings", response_model=Dict[str, SettingResponse])
async def admin_get_settings(
    admin_user: User = Depends(require_admin_user),
    db: AsyncSession = Depends(get_db),
):
    """Get all system settings."""
    service = SystemSettingService(db)
    return await service.get_settings()


# Critical security settings that cannot be modified at runtime
_PROTECTED_SETTINGS = frozenset({"SECRET_KEY", "BOT_API_SECRET"})


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
