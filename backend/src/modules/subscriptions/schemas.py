"""Subscriptions module Pydantic schemas."""
from pydantic import BaseModel
from typing import Optional, List
from datetime import datetime


class SubscriptionPlanBase(BaseModel):
    """Base subscription plan schema."""
    name: str
    description: Optional[str] = None
    price: float
    first_month_price: Optional[float] = None
    duration_days: int = 30
    features: List[str] = []


class SubscriptionPlanResponse(SubscriptionPlanBase):
    """Subscription plan response schema."""
    id: str
    is_active: bool
    created_at: datetime

    class Config:
        from_attributes = True


class SubscriptionBase(BaseModel):
    """Base subscription schema."""
    plan_id: str
    auto_renew: bool = True


class SubscriptionResponse(BaseModel):
    """Subscription response schema."""
    id: str
    user_id: str
    plan_id: str
    status: str
    start_date: datetime
    end_date: datetime
    auto_renew: bool
    next_billing_date: Optional[datetime] = None
    created_at: datetime

    class Config:
        from_attributes = True
