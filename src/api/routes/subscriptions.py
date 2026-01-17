from fastapi import APIRouter, HTTPException, status, Request, Header
from typing import Optional
import stripe

from src.models import User, Subscription, SubscriptionTier, SubscriptionStatus
from src.schemas.subscription import (
    CheckoutRequest,
    CheckoutResponse,
    PortalRequest,
    PortalResponse,
    SubscriptionResponse,
    SubscriptionStatusResponse,
    TierInfo,
    TiersResponse,
)
from src.api.deps import DbSession, CurrentUser
from src.services.stripe_service import stripe_service
from src.utils.config import get_settings

settings = get_settings()
router = APIRouter(prefix="/subscriptions", tags=["subscriptions"])


@router.get("/tiers", response_model=TiersResponse)
async def get_subscription_tiers():
    """Get available subscription tiers and their features."""
    tiers = [
        TierInfo(
            tier=SubscriptionTier.FREE,
            name="Free",
            price_monthly=0,
            features=[
                "Weekly newsletter (Friday)",
                "Access to free articles",
                "Social media content",
            ],
        ),
        TierInfo(
            tier=SubscriptionTier.PATRIOT,
            name="Patriot Subscriber",
            price_monthly=800,  # $8.00
            features=[
                "3x weekly newsletters (Mon/Wed/Fri)",
                "All articles, no paywall",
                "Source document archive",
                "Subscriber-only comments",
            ],
        ),
        TierInfo(
            tier=SubscriptionTier.WATCHDOG,
            name="Watchdog Inner Circle",
            price_monthly=3900,  # $39.00
            features=[
                "Everything in Patriot",
                "Weekly video analysis",
                "Monthly live Q&A",
                "Early access to investigations",
                "Private community access",
            ],
        ),
        TierInfo(
            tier=SubscriptionTier.FOUNDER,
            name="Founder's Circle",
            price_monthly=19900,  # $199.00
            features=[
                "Everything in Watchdog",
                "Quarterly virtual roundtable",
                "Direct messaging access",
                "Name in credits/acknowledgments",
                "Annual physical mailed report",
            ],
        ),
    ]
    return TiersResponse(tiers=tiers)


@router.get("/status", response_model=SubscriptionStatusResponse)
async def get_subscription_status(
    db: DbSession,
    user: CurrentUser,
):
    """Get current user's subscription status."""
    # Get active subscription
    subscription = (
        db.query(Subscription)
        .filter(
            Subscription.user_id == user.id,
            Subscription.status == SubscriptionStatus.ACTIVE,
        )
        .first()
    )

    return SubscriptionStatusResponse(
        tier=user.subscription_tier,
        is_active=user.subscription_tier != SubscriptionTier.FREE,
        subscription=SubscriptionResponse.model_validate(subscription) if subscription else None,
    )


@router.post("/checkout", response_model=CheckoutResponse)
async def create_checkout_session(
    request: CheckoutRequest,
    db: DbSession,
    user: CurrentUser,
):
    """Create a Stripe Checkout session to subscribe."""
    if request.tier == SubscriptionTier.FREE:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Cannot checkout for free tier",
        )

    try:
        checkout_url = await stripe_service.create_checkout_session(
            user=user,
            tier=request.tier,
            success_url=request.success_url,
            cancel_url=request.cancel_url,
            db=db,
        )
        return CheckoutResponse(checkout_url=checkout_url)
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e),
        )
    except stripe.StripeError as e:
        raise HTTPException(
            status_code=status.HTTP_502_BAD_GATEWAY,
            detail=f"Stripe error: {str(e)}",
        )


@router.post("/portal", response_model=PortalResponse)
async def create_portal_session(
    request: PortalRequest,
    db: DbSession,
    user: CurrentUser,
):
    """Create a Stripe Customer Portal session to manage subscription."""
    if not user.stripe_customer_id:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="No active subscription to manage",
        )

    try:
        portal_url = await stripe_service.create_portal_session(
            user=user,
            return_url=request.return_url,
            db=db,
        )
        return PortalResponse(portal_url=portal_url)
    except stripe.StripeError as e:
        raise HTTPException(
            status_code=status.HTTP_502_BAD_GATEWAY,
            detail=f"Stripe error: {str(e)}",
        )


@router.post("/webhook", include_in_schema=False)
async def stripe_webhook(
    request: Request,
    db: DbSession,
    stripe_signature: Optional[str] = Header(None),
):
    """Handle Stripe webhook events."""
    if not stripe_signature:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Missing Stripe signature",
        )

    payload = await request.body()

    try:
        event = stripe.Webhook.construct_event(
            payload,
            stripe_signature,
            settings.stripe_webhook_secret,
        )
    except ValueError:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid payload",
        )
    except stripe.SignatureVerificationError:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid signature",
        )

    # Handle subscription events
    if event.type == "customer.subscription.created":
        stripe_service.handle_subscription_created(event.data.object, db)
    elif event.type == "customer.subscription.updated":
        stripe_service.handle_subscription_updated(event.data.object, db)
    elif event.type == "customer.subscription.deleted":
        stripe_service.handle_subscription_deleted(event.data.object, db)
    elif event.type == "invoice.payment_succeeded":
        await handle_invoice_payment_succeeded(event.data.object, db)
    elif event.type == "invoice.payment_failed":
        await handle_invoice_payment_failed(event.data.object, db)

    return {"status": "success"}


async def handle_invoice_payment_succeeded(invoice: dict, db: DbSession) -> None:
    """Handle successful invoice payment - send receipt."""
    from src.services.notification_service import notification_service
    
    customer_id = invoice.get("customer")
    user = db.query(User).filter(User.stripe_customer_id == customer_id).first()
    
    if not user:
        return
    
    # Get subscription details
    subscription = (
        db.query(Subscription)
        .filter(Subscription.user_id == user.id)
        .order_by(Subscription.created_at.desc())
        .first()
    )
    
    tier = subscription.tier if subscription else user.subscription_tier
    amount = invoice.get("amount_paid", 0)
    invoice_id = invoice.get("id", "unknown")
    
    await notification_service.on_payment_succeeded(
        user=user,
        tier=tier,
        amount=amount,
        invoice_id=invoice_id,
    )


async def handle_invoice_payment_failed(invoice: dict, db: DbSession) -> None:
    """Handle failed invoice payment - send notification."""
    from src.services.notification_service import notification_service
    
    customer_id = invoice.get("customer")
    user = db.query(User).filter(User.stripe_customer_id == customer_id).first()
    
    if not user:
        return
    
    await notification_service.on_payment_failed(
        user=user,
        tier=user.subscription_tier,
    )
