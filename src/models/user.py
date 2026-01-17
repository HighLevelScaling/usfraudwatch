import enum
from datetime import datetime
from typing import Optional, List, TYPE_CHECKING
from sqlalchemy import String, Boolean, Enum, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from src.models.base import Base, TimestampMixin

if TYPE_CHECKING:
    from src.models.subscription import Subscription
    from src.models.article import Article


class SubscriptionTier(str, enum.Enum):
    FREE = "free"
    PATRIOT = "patriot"  # $8/month
    WATCHDOG = "watchdog"  # $39/month
    FOUNDER = "founder"  # $199/month


class User(Base, TimestampMixin):
    __tablename__ = "users"

    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    auth0_id: Mapped[str] = mapped_column(String(255), unique=True, index=True)
    email: Mapped[str] = mapped_column(String(255), unique=True, index=True)
    name: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)
    picture: Mapped[Optional[str]] = mapped_column(String(500), nullable=True)
    bio: Mapped[Optional[str]] = mapped_column(Text, nullable=True)

    # Subscription
    subscription_tier: Mapped[SubscriptionTier] = mapped_column(
        Enum(SubscriptionTier), default=SubscriptionTier.FREE
    )
    stripe_customer_id: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)

    # Admin/Author flags
    is_admin: Mapped[bool] = mapped_column(Boolean, default=False)
    is_author: Mapped[bool] = mapped_column(Boolean, default=False)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)

    # Relationships
    subscriptions: Mapped[List["Subscription"]] = relationship(
        "Subscription", back_populates="user", cascade="all, delete-orphan"
    )
    articles: Mapped[List["Article"]] = relationship(
        "Article", back_populates="author", foreign_keys="Article.author_id"
    )

    def __repr__(self) -> str:
        return f"<User {self.email}>"

    def can_access_tier(self, required_tier: SubscriptionTier) -> bool:
        """Check if user can access content requiring a specific tier."""
        tier_hierarchy = {
            SubscriptionTier.FREE: 0,
            SubscriptionTier.PATRIOT: 1,
            SubscriptionTier.WATCHDOG: 2,
            SubscriptionTier.FOUNDER: 3,
        }
        return tier_hierarchy[self.subscription_tier] >= tier_hierarchy[required_tier]
