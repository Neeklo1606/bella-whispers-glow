"""Subscriptions module API routes."""
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from typing import List

from ...core.db import get_db
from ...core.security import get_current_user_id
from .service import SubscriptionService
from .schemas import SubscriptionPlanResponse, SubscriptionResponse, SubscriptionBase

router = APIRouter()


@router.get("/plans", response_model=List[SubscriptionPlanResponse])
async def get_plans(db: AsyncSession = Depends(get_db)):
    """Get all active subscription plans."""
    service = SubscriptionService(db)
    return await service.get_plans()


@router.get("/me", response_model=SubscriptionResponse)
async def get_my_subscription(
    user_id: str = Depends(get_current_user_id),
    db: AsyncSession = Depends(get_db),
):
    """Get current user's subscription."""
    service = SubscriptionService(db)
    subscription = await service.get_user_subscription(user_id)
    if not subscription:
        raise HTTPException(status_code=404, detail="Subscription not found")
    return subscription


@router.post("/create", response_model=SubscriptionResponse)
async def create_subscription(
    subscription_data: SubscriptionBase,
    user_id: str = Depends(get_current_user_id),
    db: AsyncSession = Depends(get_db),
):
    """Create new subscription."""
    service = SubscriptionService(db)
    return await service.create_subscription(user_id, subscription_data)


@router.delete("/me", response_model=SubscriptionResponse)
async def cancel_subscription(
    user_id: str = Depends(get_current_user_id),
    db: AsyncSession = Depends(get_db),
):
    """Cancel current subscription."""
    service = SubscriptionService(db)
    subscription = await service.cancel_subscription(user_id, "")
    if not subscription:
        raise HTTPException(status_code=404, detail="Subscription not found")
    return subscription
