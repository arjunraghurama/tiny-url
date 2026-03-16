from fastapi import APIRouter, Depends, HTTPException
from fastapi.responses import RedirectResponse
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_db
from app.schemas import ShortenRequest, ShortenResponse, URLStats, URLListItem
from app.services import create_short_url, resolve_short_url, get_url_stats, get_recent_urls
from app.config import settings
from app.auth import get_current_user, get_optional_user

router = APIRouter()


@router.post("/api/shorten", response_model=ShortenResponse)
async def shorten_url(
    request: ShortenRequest,
    db: AsyncSession = Depends(get_db),
    user: dict = Depends(get_current_user),
):
    """
    Create a shortened URL. **Requires authentication.**

    Accepts a long URL and returns a short code + full short URL.
    The URL is linked to the authenticated user.
    """
    url_record = await create_short_url(db, str(request.url), user_info=user)

    return ShortenResponse(
        short_code=url_record.short_code,
        short_url=f"{settings.BASE_URL}/{url_record.short_code}",
        original_url=url_record.original_url,
        created_at=url_record.created_at,
    )


@router.get("/api/urls/recent", response_model=list[URLListItem])
async def list_recent_urls(
    db: AsyncSession = Depends(get_db),
    user: dict | None = Depends(get_optional_user),
):
    """
    Get recently created short URLs.

    - **Authenticated:** Returns the user's 10 most recent URLs.
    - **Unauthenticated:** Returns the 10 most recent global URLs.
    """
    user_id = user["sub"] if user else None
    urls = await get_recent_urls(db, user_id=user_id)
    return [
        URLListItem(
            short_code=u.short_code,
            short_url=f"{settings.BASE_URL}/{u.short_code}",
            original_url=u.original_url,
            clicks=u.clicks,
            created_at=u.created_at,
        )
        for u in urls
    ]


@router.get("/api/urls/{short_code}/stats", response_model=URLStats)
async def url_stats(short_code: str, db: AsyncSession = Depends(get_db)):
    """
    Get click statistics for a shortened URL.

    Returns the original URL, click count, creation time, and active status.
    """
    url_record = await get_url_stats(db, short_code)
    if not url_record:
        raise HTTPException(status_code=404, detail="Short URL not found")

    return URLStats(
        short_code=url_record.short_code,
        short_url=f"{settings.BASE_URL}/{url_record.short_code}",
        original_url=url_record.original_url,
        clicks=url_record.clicks,
        created_at=url_record.created_at,
        is_active=url_record.is_active,
    )


@router.get("/{short_code}")
async def redirect_to_url(short_code: str, db: AsyncSession = Depends(get_db)):
    """
    Redirect to the original URL.

    This is the main read path:
    1. Check Valkey cache (fast path, ~1ms)
    2. Fall back to PostgreSQL on cache miss (~5-10ms)
    3. Return 307 redirect to the original URL

    Uses 307 (Temporary Redirect) so browsers don't cache the redirect,
    allowing us to track clicks accurately.
    """
    original_url = await resolve_short_url(db, short_code)
    if not original_url:
        raise HTTPException(status_code=404, detail="Short URL not found")

    return RedirectResponse(url=original_url, status_code=307)
