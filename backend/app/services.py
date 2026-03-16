import uuid
import secrets
import string
import logging

from sqlalchemy import select, update
from sqlalchemy.ext.asyncio import AsyncSession

from app.models import URL, User
from app.cache import cache
from app.config import settings

logger = logging.getLogger(__name__)

# Alphanumeric character set: a-zA-Z0-9 (62 characters)
CHARSET = string.ascii_lowercase + string.ascii_uppercase + string.digits

# Maximum retries for collision handling
MAX_RETRIES = 5


def generate_short_code(length: int = None) -> str:
    """
    Generate a cryptographically random alphanumeric short code.

    Uses `secrets.choice` (not `random.choice`) for security:
    - Unpredictable: cannot be guessed or enumerated
    - Uniform distribution: each character equally likely
    - URL-safe: only a-zA-Z0-9

    For a 7-character code with 62 possible chars per position:
    62^7 = ~3.5 trillion unique combinations.
    Collision probability is negligible until billions of URLs exist.
    """
    length = length or settings.SHORT_CODE_LENGTH
    return "".join(secrets.choice(CHARSET) for _ in range(length))


async def _code_exists(db: AsyncSession, short_code: str) -> bool:
    """Check if a short code already exists in the database."""
    result = await db.execute(
        select(URL.id).where(URL.short_code == short_code)
    )
    return result.scalar_one_or_none() is not None


async def _get_or_create_user(db: AsyncSession, user_info: dict) -> User:
    """
    Get or create a User record from Keycloak token claims.

    On first login, a User row is auto-created from the JWT claims.
    On subsequent requests, the existing row is returned.
    """
    keycloak_id = uuid.UUID(user_info["sub"])

    result = await db.execute(select(User).where(User.id == keycloak_id))
    user = result.scalar_one_or_none()

    if user is None:
        user = User(
            id=keycloak_id,
            email=user_info.get("email", ""),
            username=user_info.get("preferred_username", ""),
        )
        db.add(user)
        await db.flush()
        logger.info("Created new user: %s (%s)", user.username, user.id)

    return user


async def create_short_url(
    db: AsyncSession, original_url: str, user_info: dict | None = None
) -> URL:
    """
    Create a new shortened URL with a random short code.

    Flow:
    1. Generate a random alphanumeric code (e.g., "kX9mBzQ")
    2. Check for collision (extremely rare, but possible)
    3. Link to authenticated user (if provided)
    4. Insert into PostgreSQL
    5. Cache the mapping in Valkey

    Unlike sequential Base62 encoding, random codes:
    - Cannot be enumerated (no guessing the next URL)
    - Don't reveal how many URLs have been created
    - Are uniformly distributed for better cache/DB sharding
    """
    for attempt in range(MAX_RETRIES):
        short_code = generate_short_code()

        # Check for collision (rare: ~1 in 3.5 trillion for 7 chars)
        if not await _code_exists(db, short_code):
            break
        logger.warning(f"Short code collision on attempt {attempt + 1}: {short_code}")
    else:
        raise RuntimeError("Failed to generate unique short code after max retries")

    # Resolve user if authenticated
    user_id = None
    if user_info:
        user = await _get_or_create_user(db, user_info)
        user_id = user.id

    # Insert the URL record
    url_record = URL(
        original_url=str(original_url),
        short_code=short_code,
        user_id=user_id,
    )
    db.add(url_record)
    await db.flush()

    # Cache the mapping for fast lookups
    await cache.set_url(short_code, str(original_url))

    logger.info(f"Created short URL: {short_code} -> {original_url}")
    return url_record


async def resolve_short_url(db: AsyncSession, short_code: str) -> str | None:
    """
    Resolve a short code to the original URL.

    Flow (Cache-Aside Pattern):
    1. Check Valkey cache first (fast path)
    2. On cache miss, query PostgreSQL (slow path)
    3. On DB hit, populate cache for next request
    4. Increment click counter asynchronously

    This pattern ensures:
    - Hot URLs are served from cache (~1ms)
    - Cold URLs fall back to DB (~5-10ms)
    - Cache is self-healing on misses
    """
    # Step 1: Check cache (fast path)
    cached_url = await cache.get_url(short_code)
    if cached_url:
        # Increment clicks in DB (fire-and-forget in production)
        await _increment_clicks(db, short_code)
        return cached_url

    # Step 2: Cache miss — query DB (slow path)
    result = await db.execute(
        select(URL).where(URL.short_code == short_code, URL.is_active == True)
    )
    url_record = result.scalar_one_or_none()

    if not url_record:
        return None

    # Step 3: Populate cache for next request
    await cache.set_url(short_code, url_record.original_url)

    # Step 4: Increment clicks
    await _increment_clicks(db, short_code)

    return url_record.original_url


async def get_url_stats(db: AsyncSession, short_code: str) -> URL | None:
    """Get statistics for a shortened URL."""
    result = await db.execute(
        select(URL).where(URL.short_code == short_code)
    )
    return result.scalar_one_or_none()


async def get_recent_urls(
    db: AsyncSession, limit: int = 10, user_id: str | None = None
) -> list[URL]:
    """
    Get the most recently created URLs.

    If user_id is provided, returns only that user's URLs.
    Otherwise returns the most recent global URLs.
    """
    query = select(URL)
    if user_id:
        query = query.where(URL.user_id == uuid.UUID(user_id))
    query = query.order_by(URL.created_at.desc()).limit(limit)

    result = await db.execute(query)
    return list(result.scalars().all())


async def _increment_clicks(db: AsyncSession, short_code: str):
    """Increment the click counter for a URL."""
    await db.execute(
        update(URL).where(URL.short_code == short_code).values(clicks=URL.clicks + 1)
    )
