from datetime import datetime
from typing import Optional, List
from fastapi import APIRouter, HTTPException, status, Query
from sqlalchemy import or_

from src.models import Article, ContentPillar, ArticleStatus, SubscriptionTier
from src.schemas.article import (
    ArticleCreate,
    ArticleUpdate,
    ArticlePublish,
    ArticleResponse,
    ArticleListResponse,
    ArticlePaginatedResponse,
)
from src.api.deps import DbSession, CurrentUser, CurrentUserOptional, CurrentAuthor
from src.utils.security import generate_slug

router = APIRouter(prefix="/articles", tags=["articles"])


@router.get("", response_model=ArticlePaginatedResponse)
async def list_articles(
    db: DbSession,
    user: CurrentUserOptional,
    pillar: Optional[ContentPillar] = None,
    status_filter: Optional[ArticleStatus] = Query(None, alias="status"),
    featured: Optional[bool] = None,
    search: Optional[str] = None,
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
):
    """
    List articles with filtering and pagination.
    
    - Unauthenticated users see only FREE tier published articles
    - Authenticated users see articles up to their subscription tier
    - Authors/admins can see drafts
    """
    query = db.query(Article)
    
    # Filter by status (public vs admin/author view)
    if user and (user.is_author or user.is_admin):
        if status_filter:
            query = query.filter(Article.status == status_filter)
    else:
        # Public users only see published articles
        query = query.filter(Article.status == ArticleStatus.PUBLISHED)
    
    # Filter by tier access
    if user:
        accessible_tiers = [SubscriptionTier.FREE]
        if user.subscription_tier in [SubscriptionTier.PATRIOT, SubscriptionTier.WATCHDOG, SubscriptionTier.FOUNDER]:
            accessible_tiers.append(SubscriptionTier.PATRIOT)
        if user.subscription_tier in [SubscriptionTier.WATCHDOG, SubscriptionTier.FOUNDER]:
            accessible_tiers.append(SubscriptionTier.WATCHDOG)
        if user.subscription_tier == SubscriptionTier.FOUNDER:
            accessible_tiers.append(SubscriptionTier.FOUNDER)
        query = query.filter(Article.tier_required.in_(accessible_tiers))
    else:
        query = query.filter(Article.tier_required == SubscriptionTier.FREE)
    
    # Apply filters
    if pillar:
        query = query.filter(Article.pillar == pillar)
    if featured is not None:
        query = query.filter(Article.is_featured == featured)
    if search:
        search_term = f"%{search}%"
        query = query.filter(
            or_(
                Article.title.ilike(search_term),
                Article.excerpt.ilike(search_term),
                Article.tags.ilike(search_term),
            )
        )
    
    # Get total count
    total = query.count()
    
    # Paginate
    offset = (page - 1) * page_size
    articles = (
        query
        .order_by(Article.published_at.desc().nullslast(), Article.created_at.desc())
        .offset(offset)
        .limit(page_size)
        .all()
    )
    
    pages = (total + page_size - 1) // page_size
    
    return ArticlePaginatedResponse(
        items=[ArticleListResponse.model_validate(a) for a in articles],
        total=total,
        page=page,
        page_size=page_size,
        pages=pages,
    )


@router.get("/pillars/{pillar}", response_model=ArticlePaginatedResponse)
async def list_articles_by_pillar(
    pillar: ContentPillar,
    db: DbSession,
    user: CurrentUserOptional,
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
):
    """List articles filtered by content pillar."""
    return await list_articles(
        db=db,
        user=user,
        pillar=pillar,
        page=page,
        page_size=page_size,
    )


@router.get("/{slug}", response_model=ArticleResponse)
async def get_article(
    slug: str,
    db: DbSession,
    user: CurrentUserOptional,
):
    """Get a single article by slug."""
    article = db.query(Article).filter(Article.slug == slug).first()
    
    if not article:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Article not found"
        )
    
    # Check if article is published (unless user is author/admin)
    if article.status != ArticleStatus.PUBLISHED:
        if not user or (not user.is_author and not user.is_admin):
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Article not found"
            )
    
    # Check tier access
    if user:
        if not user.can_access_tier(article.tier_required):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f"Subscription tier '{article.tier_required.value}' required"
            )
    else:
        if article.tier_required != SubscriptionTier.FREE:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Subscription required to access this article"
            )
    
    # Increment view count
    article.view_count += 1
    db.commit()
    
    return ArticleResponse.model_validate(article)


@router.post("", response_model=ArticleResponse, status_code=status.HTTP_201_CREATED)
async def create_article(
    article_data: ArticleCreate,
    db: DbSession,
    author: CurrentAuthor,
):
    """Create a new article (authors and admins only)."""
    # Generate slug if not provided
    slug = article_data.slug or generate_slug(article_data.title)
    
    # Check for duplicate slug
    existing = db.query(Article).filter(Article.slug == slug).first()
    if existing:
        # Append timestamp to make unique
        slug = f"{slug}-{int(datetime.utcnow().timestamp())}"
    
    article = Article(
        title=article_data.title,
        slug=slug,
        subtitle=article_data.subtitle,
        content=article_data.content,
        excerpt=article_data.excerpt,
        pillar=article_data.pillar,
        tags=article_data.tags,
        tier_required=article_data.tier_required,
        cover_image_url=article_data.cover_image_url,
        author_id=author.id,
        status=ArticleStatus.DRAFT,
    )
    
    db.add(article)
    db.commit()
    db.refresh(article)
    
    return ArticleResponse.model_validate(article)


@router.put("/{article_id}", response_model=ArticleResponse)
async def update_article(
    article_id: int,
    article_data: ArticleUpdate,
    db: DbSession,
    author: CurrentAuthor,
):
    """Update an article (authors and admins only)."""
    article = db.query(Article).filter(Article.id == article_id).first()
    
    if not article:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Article not found"
        )
    
    # Only allow author or admin to edit
    if article.author_id != author.id and not author.is_admin:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You can only edit your own articles"
        )
    
    # Update fields
    update_data = article_data.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(article, field, value)
    
    db.commit()
    db.refresh(article)
    
    return ArticleResponse.model_validate(article)


@router.post("/{article_id}/publish", response_model=ArticleResponse)
async def publish_article(
    article_id: int,
    publish_data: ArticlePublish,
    db: DbSession,
    author: CurrentAuthor,
):
    """Publish or unpublish an article."""
    article = db.query(Article).filter(Article.id == article_id).first()
    
    if not article:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Article not found"
        )
    
    if article.author_id != author.id and not author.is_admin:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You can only publish your own articles"
        )
    
    if publish_data.publish:
        article.status = ArticleStatus.PUBLISHED
        if not article.published_at:
            article.published_at = datetime.utcnow()
    else:
        article.status = ArticleStatus.DRAFT
    
    db.commit()
    db.refresh(article)
    
    return ArticleResponse.model_validate(article)


@router.delete("/{article_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_article(
    article_id: int,
    db: DbSession,
    author: CurrentAuthor,
):
    """Delete an article (soft delete - archives it)."""
    article = db.query(Article).filter(Article.id == article_id).first()
    
    if not article:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Article not found"
        )
    
    if article.author_id != author.id and not author.is_admin:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You can only delete your own articles"
        )
    
    # Soft delete - archive instead of hard delete
    article.status = ArticleStatus.ARCHIVED
    db.commit()
