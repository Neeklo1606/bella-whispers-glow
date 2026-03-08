"""Payments module Pydantic schemas."""
from pydantic import BaseModel
from typing import Optional
from datetime import datetime


class PaymentCreate(BaseModel):
    """Payment creation schema."""
    plan_id: str
    currency: str = "RUB"
    return_url: str = ""


class PaymentResponse(BaseModel):
    """Payment response schema."""
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
