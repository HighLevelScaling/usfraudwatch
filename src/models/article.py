import enum
from datetime import datetime
from typing import Optional, List, TYPE_CHECKING
from sqlalchemy import String, Text, Enum, ForeignKey, Boolean, Integer
from sqlalchemy.orm import Mapped, mapped_column, relationship

from src.models.base import Base, TimestampMixin
from src.models.user import SubscriptionTier

if TYPE_CHECKING:
    from src.models.user import User
    from src.models.document import SourceDocument


class ContentPillar(str, enum.Enum):
    MONEY_TRAIL = "money_trail"  # Government spending on immigration programs
    SANCTUARY = "sanctuary"  # Sanctuary city policies and outcomes
    LOOPHOLES = "loopholes"  # Asylum law exploitation
    BORDER_COMPLEX = "border_complex"  # Who profits from the system
    IMPACT = "impact"  # Real impact on American communities


class ArticleStatus(str, enum.Enum):
    DRAFT = "draft"
    PUBLISHED = "published"
    ARCHIVED = "archived"


class Article(Base, TimestampMixin):
    __tablename__ = "articles"

    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    title: Mapped[str] = mapped_column(String(500), nullable=False)
    slug: Mapped[str] = mapped_column(String(500), unique=True, index=True)
    subtitle: Mapped[Optional[str]] = mapped_column(String(500), nullable=True)
    content: Mapped[str] = mapped_column(Text, nullable=False)
    excerpt: Mapped[Optional[str]] = mapped_column(Text, nullable=True)

    # Categorization
    pillar: Mapped[ContentPillar] = mapped_column(Enum(ContentPillar), nullable=False)
    tags: Mapped[Optional[str]] = mapped_column(String(500), nullable=True)  # Comma-separated

    # Access control
    tier_required: Mapped[SubscriptionTier] = mapped_column(
        Enum(SubscriptionTier), default=SubscriptionTier.FREE
    )
    status: Mapped[ArticleStatus] = mapped_column(
        Enum(ArticleStatus), default=ArticleStatus.DRAFT
    )

    # Publishing
    published_at: Mapped[Optional[datetime]] = mapped_column(nullable=True)
    is_featured: Mapped[bool] = mapped_column(Boolean, default=False)
    view_count: Mapped[int] = mapped_column(Integer, default=0)

    # Author
    author_id: Mapped[int] = mapped_column(ForeignKey("users.id"), nullable=False)
    author: Mapped["User"] = relationship("User", back_populates="articles")

    # Cover image
    cover_image_url: Mapped[Optional[str]] = mapped_column(String(500), nullable=True)

    # Related documents
    source_documents: Mapped[List["SourceDocument"]] = relationship(
        "SourceDocument", back_populates="article", cascade="all, delete-orphan"
    )

    def __repr__(self) -> str:
        return f"<Article {self.slug}>"
