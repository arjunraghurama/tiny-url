import json
import logging

import valkey.asyncio as valkey

from app.config import settings

logger = logging.getLogger(__name__)

# Cache TTL in seconds (1 hour)
CACHE_TTL = 3600


class CacheClient:
    """Valkey (Redis-compatible) cache client for URL lookups."""

    def __init__(self):
        self.client: valkey.Valkey | None = None

    async def connect(self):
        """Initialize connection to Valkey."""
        self.client = valkey.from_url(
            settings.VALKEY_URL, decode_responses=True
        )
        logger.info("Connected to Valkey cache")

    async def close(self):
        """Close the Valkey connection."""
        if self.client:
            await self.client.close()
            logger.info("Valkey connection closed")

    async def get_url(self, short_code: str) -> str | None:
        """
        Look up the original URL by short code in cache.

        Cache-aside pattern: returns None on cache miss,
        caller is responsible for DB fallback + cache population.
        """
        try:
            cached = await self.client.get(f"url:{short_code}")
            if cached:
                logger.debug(f"Cache HIT for {short_code}")
                return cached
            logger.debug(f"Cache MISS for {short_code}")
            return None
        except Exception as e:
            logger.warning(f"Cache read error: {e}")
            return None

    async def set_url(self, short_code: str, original_url: str):
        """
        Store URL mapping in cache with TTL.

        Called after DB write (on create) or DB read (on cache miss).
        """
        try:
            await self.client.set(
                f"url:{short_code}", original_url, ex=CACHE_TTL
            )
            logger.debug(f"Cached {short_code} -> {original_url[:50]}...")
        except Exception as e:
            logger.warning(f"Cache write error: {e}")

    async def delete_url(self, short_code: str):
        """Remove a URL from cache (used when deactivating)."""
        try:
            await self.client.delete(f"url:{short_code}")
        except Exception as e:
            logger.warning(f"Cache delete error: {e}")


# Singleton instance
cache = CacheClient()
