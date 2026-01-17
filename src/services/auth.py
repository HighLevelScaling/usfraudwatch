from typing import Optional
import httpx
from jose import jwt, JWTError
from fastapi import HTTPException, status

from src.utils.config import get_settings

settings = get_settings()


class Auth0Service:
    """Service for Auth0 authentication and token validation."""

    def __init__(self):
        self.domain = settings.auth0_domain
        self.audience = settings.auth0_audience
        self.algorithms = ["RS256"]
        self._jwks: Optional[dict] = None

    async def get_jwks(self) -> dict:
        """Fetch JSON Web Key Set from Auth0."""
        if self._jwks is None:
            async with httpx.AsyncClient() as client:
                response = await client.get(
                    f"https://{self.domain}/.well-known/jwks.json"
                )
                response.raise_for_status()
                self._jwks = response.json()
        return self._jwks

    def _get_signing_key(self, jwks: dict, token: str) -> str:
        """Extract the signing key from JWKS based on token header."""
        unverified_header = jwt.get_unverified_header(token)
        
        for key in jwks.get("keys", []):
            if key.get("kid") == unverified_header.get("kid"):
                return key
        
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Unable to find appropriate key"
        )

    async def verify_token(self, token: str) -> dict:
        """Verify and decode an Auth0 JWT token."""
        try:
            jwks = await self.get_jwks()
            signing_key = self._get_signing_key(jwks, token)
            
            payload = jwt.decode(
                token,
                signing_key,
                algorithms=self.algorithms,
                audience=self.audience,
                issuer=f"https://{self.domain}/"
            )
            return payload
        
        except JWTError as e:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail=f"Invalid token: {str(e)}"
            )
        except httpx.HTTPError as e:
            raise HTTPException(
                status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
                detail=f"Auth service unavailable: {str(e)}"
            )

    def get_user_info_from_token(self, payload: dict) -> dict:
        """Extract user info from token payload."""
        return {
            "auth0_id": payload.get("sub"),
            "email": payload.get("email") or payload.get(f"{self.audience}/email"),
            "name": payload.get("name") or payload.get(f"{self.audience}/name"),
            "picture": payload.get("picture") or payload.get(f"{self.audience}/picture"),
        }


# Singleton instance
auth0_service = Auth0Service()
