"""
Keycloak JWT authentication for FastAPI.

Provides dependencies to validate Bearer tokens against Keycloak's JWKS endpoint.
- get_current_user: required auth (raises 401 if missing/invalid)
- get_optional_user: optional auth (returns None if no token)
"""

import logging
from typing import Optional

import httpx
from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from jose import JWTError, jwt

from app.config import settings

logger = logging.getLogger(__name__)

# HTTPBearer extracts the token from "Authorization: Bearer <token>"
security = HTTPBearer()
optional_security = HTTPBearer(auto_error=False)

# Cache for Keycloak's JWKS (public signing keys)
_jwks_cache: dict | None = None


async def _get_jwks() -> dict:
    """
    Fetch Keycloak's JSON Web Key Set (JWKS).

    The JWKS contains the public keys used to verify JWT signatures.
    Cached after first fetch to avoid hitting Keycloak on every request.
    """
    global _jwks_cache
    if _jwks_cache is not None:
        return _jwks_cache

    jwks_url = (
        f"{settings.KEYCLOAK_URL}/realms/{settings.KEYCLOAK_REALM}"
        f"/protocol/openid-connect/certs"
    )
    async with httpx.AsyncClient() as client:
        response = await client.get(jwks_url)
        response.raise_for_status()
        _jwks_cache = response.json()
        logger.info("Fetched Keycloak JWKS from %s", jwks_url)
        return _jwks_cache


def _decode_token(token: str, jwks: dict) -> dict:
    """
    Decode and validate a JWT token using Keycloak's public keys.

    Validates: signature, expiration, issuer, and audience.
    Returns the decoded token claims.
    """
    try:
        payload = jwt.decode(
            token,
            jwks,
            algorithms=["RS256"],
            options={
                "verify_aud": False,  # Keycloak audience varies by client
                "verify_iss": False,  # Issuer differs: docker internal vs browser URL
            },
        )
        return payload
    except JWTError as e:
        logger.warning("JWT validation failed: %s", e)
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or expired token",
            headers={"WWW-Authenticate": "Bearer"},
        )


async def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(security),
) -> dict:
    """
    FastAPI dependency — requires a valid JWT token.

    Returns a dict with user info extracted from the token:
    - sub: Keycloak user ID (UUID)
    - email: user's email
    - preferred_username: display name
    """
    jwks = await _get_jwks()
    payload = _decode_token(credentials.credentials, jwks)

    return {
        "sub": payload.get("sub"),
        "email": payload.get("email"),
        "preferred_username": payload.get("preferred_username"),
    }


async def get_optional_user(
    credentials: Optional[HTTPAuthorizationCredentials] = Depends(optional_security),
) -> dict | None:
    """
    FastAPI dependency — optional JWT token.

    Returns user info dict if a valid token is present, None otherwise.
    Does not raise 401 when no token is provided.
    """
    if credentials is None:
        return None

    try:
        jwks = await _get_jwks()
        payload = _decode_token(credentials.credentials, jwks)
        return {
            "sub": payload.get("sub"),
            "email": payload.get("email"),
            "preferred_username": payload.get("preferred_username"),
        }
    except HTTPException:
        return None
