"""Subscriptions module Pydantic schemas."""
from pydantic import BaseModel, field_validator
from typing import Optional, List
from datetime import datetime


def _coerce_uuid(v):
    return str(v) if v is not None else None


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

    @field_validator("id", "user_id", "plan_id", "status", mode="before")
    @classmethod
    def coerce_ids(cls, v):
        if v is None:
            return None
        if hasattr(v, "value"):  # enum (status)
            return v.value
        return str(v)

    id: str
    user_id: str
    plan_id: Optional[str] = None
    status: str
    start_date: Optional[datetime] = None
    end_date: Optional[datetime] = None
    auto_renew: bool = True
    next_billing_date: Optional[datetime] = None
    created_at: datetime

    class Config:
        from_attributes = True
