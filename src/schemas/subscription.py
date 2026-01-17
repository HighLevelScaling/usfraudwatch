from datetime import datetime
from typing import Optional
from pydantic import BaseModel, HttpUrl

from src.models.user import SubscriptionTier
from src.models.subscription import SubscriptionStatus


class CheckoutRequest(BaseModel):
    """Request to create a checkout session."""
    tier: SubscriptionTier
    success_url: str
    cancel_url: str


class CheckoutResponse(BaseModel):
    """Response with checkout session URL."""
    checkout_url: str


class PortalRequest(BaseModel):
    """Request to create a customer portal session."""
    return_url: str


class PortalResponse(BaseModel):
    """Response with customer portal URL."""
    portal_url: str


class SubscriptionResponse(BaseModel):
    """Current subscription status."""
    id: int
    tier: SubscriptionTier
    status: SubscriptionStatus
    current_period_start: Optional[datetime]
    current_period_end: Optional[datetime]
    canceled_at: Optional[datetime]

    class Config:
        from_attributes = True


class SubscriptionStatusResponse(BaseModel):
    """User's subscription status summary."""
    tier: SubscriptionTier
    is_active: bool
    subscription: Optional[SubscriptionResponse]


class TierInfo(BaseModel):
    """Information about a subscription tier."""
    tier: SubscriptionTier
    name: str
    price_monthly: int  # in cents
    features: list[str]


class TiersResponse(BaseModel):
    """List of available subscription tiers."""
    tiers: list[TierInfo]
