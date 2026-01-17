from datetime import datetime
from typing import Optional, List
from pydantic import BaseModel, Field

from src.models.article import ContentPillar, ArticleStatus
from src.models.user import SubscriptionTier


class ArticleBase(BaseModel):
    title: str = Field(..., min_length=1, max_length=500)
    subtitle: Optional[str] = Field(None, max_length=500)
    content: str = Field(..., min_length=1)
    excerpt: Optional[str] = None
    pillar: ContentPillar
    tags: Optional[str] = Field(None, max_length=500)
    tier_required: SubscriptionTier = SubscriptionTier.FREE
    cover_image_url: Optional[str] = None


class ArticleCreate(ArticleBase):
    """Schema for creating a new article."""
    slug: Optional[str] = Field(None, max_length=500)  # Auto-generated if not provided


class ArticleUpdate(BaseModel):
    """Schema for updating an article."""
    title: Optional[str] = Field(None, min_length=1, max_length=500)
    subtitle: Optional[str] = Field(None, max_length=500)
    content: Optional[str] = None
    excerpt: Optional[str] = None
    pillar: Optional[ContentPillar] = None
    tags: Optional[str] = Field(None, max_length=500)
    tier_required: Optional[SubscriptionTier] = None
    status: Optional[ArticleStatus] = None
    is_featured: Optional[bool] = None
    cover_image_url: Optional[str] = None


class ArticlePublish(BaseModel):
    """Schema for publishing an article."""
    publish: bool = True


class AuthorResponse(BaseModel):
    """Minimal author info for article responses."""
    id: int
    name: Optional[str]
    picture: Optional[str]

    class Config:
        from_attributes = True


class ArticleResponse(BaseModel):
    """Schema for article response."""
    id: int
    title: str
    slug: str
    subtitle: Optional[str]
    content: str
    excerpt: Optional[str]
    pillar: ContentPillar
    tags: Optional[str]
    tier_required: SubscriptionTier
    status: ArticleStatus
    published_at: Optional[datetime]
    is_featured: bool
    view_count: int
    cover_image_url: Optional[str]
    author: AuthorResponse
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class ArticleListResponse(BaseModel):
    """Schema for article list item (without full content)."""
    id: int
    title: str
    slug: str
    subtitle: Optional[str]
    excerpt: Optional[str]
    pillar: ContentPillar
    tier_required: SubscriptionTier
    status: ArticleStatus
    published_at: Optional[datetime]
    is_featured: bool
    view_count: int
    cover_image_url: Optional[str]
    author: AuthorResponse
    created_at: datetime

    class Config:
        from_attributes = True


class ArticlePaginatedResponse(BaseModel):
    """Paginated list of articles."""
    items: List[ArticleListResponse]
    total: int
    page: int
    page_size: int
    pages: int
