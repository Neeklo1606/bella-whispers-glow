"""Payments module Pydantic schemas."""
from pydantic import BaseModel, field_validator
from typing import Optional
from datetime import datetime


def _coerce_uuid(v):
    """Convert UUID to str for JSON serialization."""
    return str(v) if v is not None else None


class PaymentCreate(BaseModel):
    """Payment creation schema."""
    plan_id: str
    currency: str = "RUB"
    return_url: str = ""


class PaymentResponse(BaseModel):
    """Payment response schema."""

    @field_validator("id", "user_id", "plan_id", "subscription_id", mode="before")
    @classmethod
    def coerce_ids(cls, v):
        return _coerce_uuid(v)

    id: str
    user_id: str
    plan_id: Optional[str] = None
    subscription_id: Optional[str] = None
    amount: float
    currency: str
    status: str
    provider: str
    payment_url: Optional[str] = None
    paid_at: Optional[datetime] = None
    created_at: datetime

    class Config:
        from_attributes = True


class PaymentWebhook(BaseModel):
    """Payment webhook schema."""
    event: str
    object: dict
    signature: Optional[str] = None
