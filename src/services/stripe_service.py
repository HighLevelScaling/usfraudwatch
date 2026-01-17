from datetime import datetime
from typing import Optional
import stripe
from sqlalchemy.orm import Session
import asyncio

from src.utils.config import get_settings
from src.models import User, Subscription, SubscriptionTier, SubscriptionStatus

settings = get_settings()
stripe.api_key = settings.stripe_secret_key

# Import notification service lazily to avoid circular imports
def get_notification_service():
    from src.services.notification_service import notification_service
    return notification_service


class StripeService:
    """Service for Stripe subscription management."""

    TIER_TO_PRICE = {
        SubscriptionTier.PATRIOT: settings.stripe_price_patriot,
        SubscriptionTier.WATCHDOG: settings.stripe_price_watchdog,
        SubscriptionTier.FOUNDER: settings.stripe_price_founder,
    }

    PRICE_TO_TIER = {v: k for k, v in TIER_TO_PRICE.items() if v}

    @staticmethod
    async def get_or_create_customer(user: User, db: Session) -> str:
        """Get or create a Stripe customer for a user."""
        if user.stripe_customer_id:
            return user.stripe_customer_id

        customer = stripe.Customer.create(
            email=user.email,
            name=user.name,
            metadata={"user_id": str(user.id), "auth0_id": user.auth0_id}
        )

        user.stripe_customer_id = customer.id
        db.commit()

        return customer.id

    @staticmethod
    async def create_checkout_session(
        user: User,
        tier: SubscriptionTier,
        success_url: str,
        cancel_url: str,
        db: Session,
    ) -> str:
        """Create a Stripe Checkout session for subscription."""
        if tier == SubscriptionTier.FREE:
            raise ValueError("Cannot create checkout for free tier")

        price_id = StripeService.TIER_TO_PRICE.get(tier)
        if not price_id:
            raise ValueError(f"No price configured for tier: {tier}")

        customer_id = await StripeService.get_or_create_customer(user, db)

        session = stripe.checkout.Session.create(
            customer=customer_id,
            payment_method_types=["card"],
            line_items=[{"price": price_id, "quantity": 1}],
            mode="subscription",
            success_url=success_url,
            cancel_url=cancel_url,
            metadata={"user_id": str(user.id), "tier": tier.value},
        )

        return session.url

    @staticmethod
    async def create_portal_session(user: User, return_url: str, db: Session) -> str:
        """Create a Stripe Customer Portal session."""
        if not user.stripe_customer_id:
            raise ValueError("User has no Stripe customer ID")

        session = stripe.billing_portal.Session.create(
            customer=user.stripe_customer_id,
            return_url=return_url,
        )

        return session.url

    @staticmethod
    def handle_subscription_created(
        stripe_subscription: stripe.Subscription,
        db: Session,
    ) -> Optional[Subscription]:
        """Handle subscription.created webhook event."""
        customer_id = stripe_subscription.customer
        user = db.query(User).filter(User.stripe_customer_id == customer_id).first()

        if not user:
            return None

        price_id = stripe_subscription["items"]["data"][0]["price"]["id"]
        tier = StripeService.PRICE_TO_TIER.get(price_id, SubscriptionTier.PATRIOT)

        subscription = Subscription(
            user_id=user.id,
            stripe_subscription_id=stripe_subscription.id,
            stripe_price_id=price_id,
            tier=tier,
            status=SubscriptionStatus(stripe_subscription.status),
            current_period_start=datetime.fromtimestamp(
                stripe_subscription.current_period_start
            ),
            current_period_end=datetime.fromtimestamp(
                stripe_subscription.current_period_end
            ),
        )

        db.add(subscription)
        user.subscription_tier = tier
        db.commit()
        db.refresh(subscription)

        # Send notification (run in background)
        try:
            notification = get_notification_service()
            amount = StripeService._get_tier_amount(tier)
            asyncio.create_task(notification.on_subscription_created(user, tier, amount))
        except Exception as e:
            print(f"Failed to send subscription notification: {e}")

        return subscription

    @staticmethod
    def handle_subscription_updated(
        stripe_subscription: stripe.Subscription,
        db: Session,
    ) -> Optional[Subscription]:
        """Handle subscription.updated webhook event."""
        subscription = (
            db.query(Subscription)
            .filter(Subscription.stripe_subscription_id == stripe_subscription.id)
            .first()
        )

        if not subscription:
            return None

        price_id = stripe_subscription["items"]["data"][0]["price"]["id"]
        tier = StripeService.PRICE_TO_TIER.get(price_id, subscription.tier)

        subscription.stripe_price_id = price_id
        subscription.tier = tier
        subscription.status = SubscriptionStatus(stripe_subscription.status)
        subscription.current_period_start = datetime.fromtimestamp(
            stripe_subscription.current_period_start
        )
        subscription.current_period_end = datetime.fromtimestamp(
            stripe_subscription.current_period_end
        )

        # Update user tier and send notifications
        user = subscription.user
        old_tier = user.subscription_tier
        
        if stripe_subscription.status == "active":
            user.subscription_tier = tier
            # Check for upgrade/downgrade
            if old_tier != tier:
                try:
                    notification = get_notification_service()
                    if StripeService._tier_rank(tier) > StripeService._tier_rank(old_tier):
                        asyncio.create_task(notification.on_subscription_upgraded(user, old_tier, tier))
                    else:
                        asyncio.create_task(notification.on_subscription_downgraded(user, old_tier, tier))
                except Exception as e:
                    print(f"Failed to send tier change notification: {e}")
        elif stripe_subscription.status in ["canceled", "unpaid"]:
            user.subscription_tier = SubscriptionTier.FREE
        elif stripe_subscription.status == "past_due":
            try:
                notification = get_notification_service()
                asyncio.create_task(notification.on_payment_failed(user, tier))
            except Exception as e:
                print(f"Failed to send payment failed notification: {e}")

        db.commit()
        db.refresh(subscription)

        return subscription

    @staticmethod
    def handle_subscription_deleted(
        stripe_subscription: stripe.Subscription,
        db: Session,
    ) -> Optional[Subscription]:
        """Handle subscription.deleted webhook event."""
        subscription = (
            db.query(Subscription)
            .filter(Subscription.stripe_subscription_id == stripe_subscription.id)
            .first()
        )

        if not subscription:
            return None

        subscription.status = SubscriptionStatus.CANCELED
        subscription.canceled_at = datetime.utcnow()

        # Downgrade user to free tier
        user = subscription.user
        old_tier = user.subscription_tier
        user.subscription_tier = SubscriptionTier.FREE

        # Send cancellation notification
        try:
            notification = get_notification_service()
            end_date = subscription.current_period_end or datetime.utcnow()
            asyncio.create_task(notification.on_subscription_canceled(user, old_tier, end_date))
        except Exception as e:
            print(f"Failed to send cancellation notification: {e}")

        db.commit()
        db.refresh(subscription)

        return subscription

    @staticmethod
    def _get_tier_amount(tier: SubscriptionTier) -> int:
        """Get price in cents for a tier."""
        amounts = {
            SubscriptionTier.PATRIOT: 800,
            SubscriptionTier.WATCHDOG: 3900,
            SubscriptionTier.FOUNDER: 19900,
        }
        return amounts.get(tier, 0)

    @staticmethod
    def _tier_rank(tier: SubscriptionTier) -> int:
        """Get tier rank for comparison."""
        ranks = {
            SubscriptionTier.FREE: 0,
            SubscriptionTier.PATRIOT: 1,
            SubscriptionTier.WATCHDOG: 2,
            SubscriptionTier.FOUNDER: 3,
        }
        return ranks.get(tier, 0)


stripe_service = StripeService()
