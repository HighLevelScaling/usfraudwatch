from typing import Optional, Annotated
import asyncio
from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from sqlalchemy.orm import Session

from src.models import get_db, User, SubscriptionTier
from src.services.auth import auth0_service

# Security scheme
security = HTTPBearer(auto_error=False)


async def get_current_user_optional(
    credentials: Annotated[Optional[HTTPAuthorizationCredentials], Depends(security)],
    db: Annotated[Session, Depends(get_db)]
) -> Optional[User]:
    """Get current user if authenticated, None otherwise."""
    if credentials is None:
        return None
    
    token = credentials.credentials
    payload = await auth0_service.verify_token(token)
    user_info = auth0_service.get_user_info_from_token(payload)
    
    # Find or create user
    user = db.query(User).filter(User.auth0_id == user_info["auth0_id"]).first()
    
    if user is None:
        # Create new user on first login
        user = User(
            auth0_id=user_info["auth0_id"],
            email=user_info["email"],
            name=user_info.get("name"),
            picture=user_info.get("picture"),
            subscription_tier=SubscriptionTier.FREE
        )
        db.add(user)
        db.commit()
        db.refresh(user)
        
        # Send welcome email (async, don't wait)
        try:
            from src.services.notification_service import notification_service
            asyncio.create_task(notification_service.on_user_signup(user))
        except Exception as e:
            print(f"Failed to send welcome email: {e}")
    
    if not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="User account is deactivated"
        )
    
    return user


async def get_current_user(
    user: Annotated[Optional[User], Depends(get_current_user_optional)]
) -> User:
    """Get current user, raise 401 if not authenticated."""
    if user is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Not authenticated",
            headers={"WWW-Authenticate": "Bearer"}
        )
    return user


async def get_current_admin(
    user: Annotated[User, Depends(get_current_user)]
) -> User:
    """Get current user and verify they are an admin."""
    if not user.is_admin:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Admin access required"
        )
    return user


async def get_current_author(
    user: Annotated[User, Depends(get_current_user)]
) -> User:
    """Get current user and verify they are an author or admin."""
    if not user.is_author and not user.is_admin:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Author access required"
        )
    return user


def require_tier(minimum_tier: SubscriptionTier):
    """Factory for tier-checking dependency."""
    async def tier_checker(
        user: Annotated[User, Depends(get_current_user)]
    ) -> User:
        if not user.can_access_tier(minimum_tier):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f"Subscription tier '{minimum_tier.value}' or higher required"
            )
        return user
    return tier_checker


# Pre-built tier dependencies
RequirePatriot = Depends(require_tier(SubscriptionTier.PATRIOT))
RequireWatchdog = Depends(require_tier(SubscriptionTier.WATCHDOG))
RequireFounder = Depends(require_tier(SubscriptionTier.FOUNDER))


# Type aliases for cleaner route signatures
CurrentUser = Annotated[User, Depends(get_current_user)]
CurrentUserOptional = Annotated[Optional[User], Depends(get_current_user_optional)]
CurrentAdmin = Annotated[User, Depends(get_current_admin)]
CurrentAuthor = Annotated[User, Depends(get_current_author)]
DbSession = Annotated[Session, Depends(get_db)]
