"""
Notification service for automated email triggers.
Integrates with email_service to send automated notifications.
"""
from datetime import datetime
from typing import Optional
from sqlalchemy.orm import Session

from src.models import User, Article, SubscriptionTier
from src.services.email_service import email_service


class NotificationService:
    """Service for triggering automated notifications."""

    # ==================== USER LIFECYCLE ====================

    @staticmethod
    async def on_user_signup(user: User) -> None:
        """Triggered when a new user signs up."""
        await email_service.send_welcome_email(
            to_email=user.email,
            name=user.name,
            tier=user.subscription_tier.value,
        )
        # Notify admin
        await email_service.notify_admin_new_signup(
            user_email=user.email,
            tier=user.subscription_tier.value,
        )

    @staticmethod
    async def on_email_verification_requested(user: User, verification_link: str) -> None:
        """Triggered when email verification is requested."""
        await email_service.send_email_verification(
            to_email=user.email,
            name=user.name,
            verification_link=verification_link,
        )

    @staticmethod
    async def on_password_reset_requested(user: User, reset_link: str) -> None:
        """Triggered when password reset is requested."""
        await email_service.send_password_reset(
            to_email=user.email,
            name=user.name,
            reset_link=reset_link,
        )

    # ==================== SUBSCRIPTION LIFECYCLE ====================

    @staticmethod
    async def on_subscription_created(user: User, tier: SubscriptionTier, amount: int) -> None:
        """Triggered when a subscription is created/purchased."""
        await email_service.send_subscription_confirmation(
            to_email=user.email,
            name=user.name,
            tier=tier.value,
            amount=amount,
        )

    @staticmethod
    async def on_subscription_upgraded(user: User, old_tier: SubscriptionTier, new_tier: SubscriptionTier) -> None:
        """Triggered when subscription is upgraded."""
        await email_service.send_subscription_upgraded(
            to_email=user.email,
            name=user.name,
            old_tier=old_tier.value,
            new_tier=new_tier.value,
        )

    @staticmethod
    async def on_subscription_downgraded(user: User, old_tier: SubscriptionTier, new_tier: SubscriptionTier) -> None:
        """Triggered when subscription is downgraded."""
        await email_service.send_subscription_downgraded(
            to_email=user.email,
            name=user.name,
            old_tier=old_tier.value,
            new_tier=new_tier.value,
        )

    @staticmethod
    async def on_subscription_canceled(user: User, tier: SubscriptionTier, end_date: datetime) -> None:
        """Triggered when subscription is canceled."""
        await email_service.send_subscription_canceled(
            to_email=user.email,
            name=user.name,
            tier=tier.value,
            end_date=end_date,
        )

    @staticmethod
    async def on_trial_ending(user: User, days_left: int) -> None:
        """Triggered when trial is about to end."""
        await email_service.send_trial_ending_reminder(
            to_email=user.email,
            name=user.name,
            days_left=days_left,
        )

    # ==================== PAYMENT EVENTS ====================

    @staticmethod
    async def on_payment_succeeded(user: User, tier: SubscriptionTier, amount: int, invoice_id: str) -> None:
        """Triggered when payment succeeds."""
        await email_service.send_payment_receipt(
            to_email=user.email,
            name=user.name,
            tier=tier.value,
            amount=amount,
            invoice_id=invoice_id,
        )

    @staticmethod
    async def on_payment_failed(user: User, tier: SubscriptionTier) -> None:
        """Triggered when payment fails."""
        await email_service.send_payment_failed(
            to_email=user.email,
            name=user.name,
            tier=tier.value,
        )

    # ==================== CONTENT EVENTS ====================

    @staticmethod
    async def on_article_published(article: Article, subscribers: list[User]) -> dict:
        """Triggered when an article is published. Notifies eligible subscribers."""
        sent = 0
        failed = 0

        for user in subscribers:
            # Check if user can access this article's tier
            if user.can_access_tier(article.tier_required):
                success = await email_service.send_new_article_notification(
                    to_email=user.email,
                    name=user.name,
                    article_title=article.title,
                    article_excerpt=article.excerpt or article.content[:200] + "...",
                    article_url=f"{email_service.SITE_URL}/articles/{article.slug}",
                )
                if success:
                    sent += 1
                else:
                    failed += 1

        return {"sent": sent, "failed": failed}

    # ==================== SUPPORT EVENTS ====================

    @staticmethod
    async def on_support_ticket_created(
        user: User,
        ticket_id: str,
        subject: str,
        message: str,
    ) -> None:
        """Triggered when a support ticket is created."""
        # Send confirmation to user
        await email_service.send_support_confirmation(
            to_email=user.email,
            name=user.name,
            ticket_id=ticket_id,
            subject_line=subject,
        )
        # Notify admin
        await email_service.notify_admin_support_request(
            user_email=user.email,
            ticket_id=ticket_id,
            subject_line=subject,
            message=message,
        )

    @staticmethod
    async def on_support_reply(
        user: User,
        ticket_id: str,
        reply_content: str,
    ) -> None:
        """Triggered when support replies to a ticket."""
        await email_service.send_support_reply(
            to_email=user.email,
            name=user.name,
            ticket_id=ticket_id,
            reply_content=reply_content,
        )


notification_service = NotificationService()
