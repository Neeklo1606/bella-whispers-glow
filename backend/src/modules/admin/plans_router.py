"""Admin plans (subscription tariffs) API routes."""
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from typing import Optional, List
from uuid import UUID
from pydantic import BaseModel

from ...core.db import get_db
from ...core.security import require_admin_user
from ...modules.users.models import User
from ...modules.subscriptions.repository import SubscriptionPlanRepository
from ...modules.subscriptions.models import SubscriptionPlan


router = APIRouter()


class PlanCreate(BaseModel):
    """Create plan request."""
    name: str
    description: Optional[str] = None
    price: float
    first_month_price: Optional[float] = None
    duration_days: int = 30
    features: Optional[List] = None
    currency: str = "RUB"
    is_active: bool = True


class PlanUpdate(BaseModel):
    """Update plan request."""
    name: Optional[str] = None
    description: Optional[str] = None
    price: Optional[float] = None
    first_month_price: Optional[float] = None
    duration_days: Optional[int] = None
    features: Optional[List] = None
    currency: Optional[str] = None
    is_active: Optional[bool] = None


def _plan_to_response(plan: SubscriptionPlan) -> dict:
    """Convert plan model to response dict."""
    return {
        "id": str(plan.id),
        "name": plan.name,
        "description": plan.description,
        "price": float(plan.price),
        "first_month_price": float(plan.first_month_price) if plan.first_month_price is not None else None,
        "duration_days": plan.duration_days,
        "features": plan.features or [],
        "currency": plan.currency,
        "is_active": plan.is_active,
    }


@router.get("", response_model=List[dict])
async def get_plans(
    admin_user: User = Depends(require_admin_user),
    db: AsyncSession = Depends(get_db),
):
    """Get all subscription plans (active and inactive)."""
    repo = SubscriptionPlanRepository(db)
    plans = await repo.get_all()
    return [_plan_to_response(p) for p in plans]


@router.post("", response_model=dict)
async def create_plan(
    data: PlanCreate,
    admin_user: User = Depends(require_admin_user),
    db: AsyncSession = Depends(get_db),
):
    """Create new subscription plan."""
    repo = SubscriptionPlanRepository(db)
    plan_data = {
        "name": data.name,
        "description": data.description,
        "price": data.price,
        "first_month_price": data.first_month_price,
        "duration_days": data.duration_days,
        "features": data.features if data.features is not None else [],
        "currency": data.currency,
        "is_active": data.is_active,
    }
    plan = await repo.create(plan_data)
    return _plan_to_response(plan)


@router.put("/{plan_id}", response_model=dict)
async def update_plan(
    plan_id: str,
    data: PlanUpdate,
    admin_user: User = Depends(require_admin_user),
    db: AsyncSession = Depends(get_db),
):
    """Update subscription plan."""
    repo = SubscriptionPlanRepository(db)
    plan = await repo.get_by_id(UUID(plan_id))
    if not plan:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Plan not found",
        )
    update_data = data.model_dump(exclude_unset=True)
    plan = await repo.update(UUID(plan_id), update_data)
    if not plan:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Plan not found",
        )
    return _plan_to_response(plan)


@router.delete("/{plan_id}")
async def delete_plan(
    plan_id: str,
    admin_user: User = Depends(require_admin_user),
    db: AsyncSession = Depends(get_db),
):
    """Delete subscription plan."""
    repo = SubscriptionPlanRepository(db)
    deleted = await repo.delete(UUID(plan_id))
    if not deleted:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Plan not found",
        )
    return {"success": True, "message": "Plan deleted"}
