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
import uuid
from uuid import UUID

from ...core.db import get_db
from ...core.security import require_admin_user
from ...modules.system_settings.service import SystemSettingService
from ...modules.system_settings.schemas import SettingResponse, SettingUpdate
from ...modules.users.models import User
from ...modules.users.schemas import UserResponse, AdminUserCreate, AdminUserUpdate
from ...modules.users.enums import UserRole
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


@router.get("/payments/stats")
async def admin_get_payment_stats(
    admin_user: User = Depends(require_admin_user),
    db: AsyncSession = Depends(get_db),
):
    """Get payment statistics (revenue, counts by status, by period)."""
    from ...modules.payments.models import Payment, PaymentStatus
    today = date.today()
    week_ago = today - timedelta(days=7)
    month_ago = today - timedelta(days=30)

    # Total completed revenue
    total_rev = await db.execute(
        select(func.coalesce(func.sum(Payment.amount), 0)).where(
            Payment.status == PaymentStatus.COMPLETED
        )
    )
    total_revenue = float(total_rev.scalar() or 0)

    # Counts by status
    status_counts = {}
    for st in PaymentStatus:
        r = await db.execute(select(func.count(Payment.id)).where(Payment.status == st))
        status_counts[st.value] = r.scalar() or 0

    # Revenue today
    rev_today_r = await db.execute(
        select(func.coalesce(func.sum(Payment.amount), 0)).where(
            func.date(Payment.created_at) == today,
            Payment.status == PaymentStatus.COMPLETED,
        )
    )
    revenue_today = float(rev_today_r.scalar() or 0)

    # Revenue this week
    rev_week_r = await db.execute(
        select(func.coalesce(func.sum(Payment.amount), 0)).where(
            func.date(Payment.created_at) >= week_ago,
            Payment.status == PaymentStatus.COMPLETED,
        )
    )
    revenue_week = float(rev_week_r.scalar() or 0)

    # Revenue this month
    rev_month_r = await db.execute(
        select(func.coalesce(func.sum(Payment.amount), 0)).where(
            func.date(Payment.created_at) >= month_ago,
            Payment.status == PaymentStatus.COMPLETED,
        )
    )
    revenue_month = float(rev_month_r.scalar() or 0)

    # Count payments today
    cnt_today_r = await db.execute(
        select(func.count(Payment.id)).where(func.date(Payment.created_at) == today)
    )
    payments_today = cnt_today_r.scalar() or 0

    # Total count
    total_cnt_r = await db.execute(select(func.count(Payment.id)))
    total_payments = total_cnt_r.scalar() or 0

    return {
        "total_revenue": total_revenue,
        "total_payments": total_payments,
        "revenue_today": revenue_today,
        "revenue_week": revenue_week,
        "revenue_month": revenue_month,
        "payments_today": payments_today,
        "by_status": status_counts,
    }


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
    return [UserResponse.model_validate(u) for u in users]


@router.post("/users", response_model=UserResponse)
async def admin_create_user(
    data: AdminUserCreate,
    admin_user: User = Depends(require_admin_user),
    db: AsyncSession = Depends(get_db),
):
    """Create admin user for admin panel access."""
    if data.role not in (UserRole.ADMIN, UserRole.SUPER_ADMIN):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Role must be admin or super_admin for admin panel access",
        )
    user_repo = UserRepository(db)
    existing = await user_repo.get_by_email(data.email)
    if existing:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Email already registered")
    user = await user_repo.create({
        "email": data.email,
        "password": data.password,
        "first_name": data.first_name,
        "last_name": data.last_name,
        "role": data.role,
    })
    await db.commit()
    await db.refresh(user)
    return UserResponse.model_validate(user)


@router.delete("/users/{user_id}")
async def admin_delete_user(
    user_id: str,
    admin_user: User = Depends(require_admin_user),
    db: AsyncSession = Depends(get_db),
):
    """Delete user. Cannot delete current admin."""
    target_id = UUID(user_id)
    if target_id == admin_user.id:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Cannot delete yourself",
        )
    user_repo = UserRepository(db)
    deleted = await user_repo.delete(target_id)
    if not deleted:
        raise HTTPException(status_code=404, detail="User not found")
    await db.commit()
    return {"success": True, "message": "User deleted"}


@router.patch("/users/{user_id}", response_model=UserResponse)
async def admin_update_user(
    user_id: str,
    data: AdminUserUpdate,
    admin_user: User = Depends(require_admin_user),
    db: AsyncSession = Depends(get_db),
):
    """Update user role or password."""
    user_repo = UserRepository(db)
    user = await user_repo.get_by_id(UUID(user_id))
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    updates = {}
    if data.role is not None:
        updates["role"] = data.role
    if data.password is not None and len(data.password) >= 6:
        updates["password"] = data.password
    if not updates:
        await db.refresh(user)
        return UserResponse.model_validate(user)
    await user_repo.update(user.id, updates)
    await db.commit()
    await db.refresh(user)
    return UserResponse.model_validate(user)
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
_DEFAULT_YOOKASSA_SHOP_ID = "1294766"
_DEFAULT_YOOKASSA_SECRET_KEY = "live_dARehpUSwWdmqXUV9q5NNI_ys_hdVqdBzTujqkBfk6U"


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
    """Test YooKassa. Order: system_settings -> env -> hardcoded defaults."""
    from ...core.config import settings as app_settings
    service = SystemSettingService(db)
    db_settings = await service.get_settings()

    def get_val(key: str) -> str:
        s = db_settings.get(key)
        if s and s.value is not None:
            v = str(s.value).strip()
            if v:
                return v
        if key == "YOOKASSA_SHOP_ID":
            v = (app_settings.YOOKASSA_SHOP_ID or "").strip()
            return v or _DEFAULT_YOOKASSA_SHOP_ID
        if key == "YOOKASSA_SECRET_KEY":
            v = (app_settings.YOOKASSA_SECRET_KEY or "").strip()
            return v or _DEFAULT_YOOKASSA_SECRET_KEY
        return ""

    shop_id = get_val("YOOKASSA_SHOP_ID")
    secret = get_val("YOOKASSA_SECRET_KEY")
    
    import httpx
    import base64
    try:
        auth = base64.b64encode(f"{shop_id}:{secret}".encode()).decode()
        async with httpx.AsyncClient() as client:
            r = await client.post(
                "https://api.yookassa.ru/v3/payments",
                headers={"Authorization": f"Basic {auth}", "Idempotence-Key": str(uuid.uuid4())},
                json={
                    "amount": {"value": "1.00", "currency": "RUB"},
                    "capture": True,
                    "description": "Admin test",
                    "confirmation": {"type": "redirect", "return_url": "https://app.bellahasias.ru/admin/settings"},
                },
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
