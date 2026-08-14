"""Redis Cache Connection Lifecycle Manager & Cache Helper.

Provides async Redis client initialization, ping verification, key-value cache operations,
graceful connection cleanup, and FastAPI dependency helpers matching Section 8.2 & 8.3 requirements.
"""

import logging
from typing import AsyncGenerator, Optional
import redis.asyncio as aioredis
from app.config import settings

logger = logging.getLogger("app.db.redis")


class RedisManager:
    """Async Redis connection manager encapsulating cache client lifecycle and helper methods."""

    def __init__(self):
        self.client: Optional[aioredis.Redis] = None

    async def connect(self) -> None:
        """Initialize async Redis client, ping host, and verify connectivity."""
        logger.info("Initializing Redis connection to '%s'...", settings.REDIS_URL)
        try:
            self.client = aioredis.Redis.from_url(
                settings.REDIS_URL,
                decode_responses=True,
                socket_timeout=2.0,
            )
            # Verify connection via ping command
            await self.client.ping()
            logger.info("Redis connection ping successful! URL: '%s'", settings.REDIS_URL)
        except Exception as exc:
            logger.warning("Redis ping failed or host unreachable (%s). Redis manager operating in disconnected/fallback state.", exc)

    async def close(self) -> None:
        """Close async Redis client connection on application shutdown."""
        if self.client is not None:
            logger.info("Closing Redis client connection...")
            try:
                await self.client.aclose()
            except AttributeError:
                await self.client.close()
            self.client = None
            logger.info("Redis connection closed cleanly.")

    async def get(self, key: str) -> Optional[str]:
        """Retrieve cached string value for the given key."""
        if self.client is None:
            return None
        try:
            return await self.client.get(key)
        except Exception as exc:
            logger.warning("Redis GET failed for key '%s': %s", key, exc)
            return None

    async def set(
        self, key: str, value: str, expire_seconds: Optional[int] = None
    ) -> bool:
        """Store key-value pair in Redis with optional expiration time in seconds."""
        if self.client is None:
            return False
        try:
            return bool(await self.client.set(key, value, ex=expire_seconds))
        except Exception as exc:
            logger.warning("Redis SET failed for key '%s': %s", key, exc)
            return False

    async def delete(self, key: str) -> bool:
        """Delete key from Redis cache."""
        if self.client is None:
            return False
        try:
            return bool(await self.client.delete(key))
        except Exception as exc:
            logger.warning("Redis DELETE failed for key '%s': %s", key, exc)
            return False


# Global singleton Redis manager instance
redis_manager = RedisManager()


async def get_redis() -> AsyncGenerator[Optional[aioredis.Redis], None]:
    """FastAPI dependency yielding active Redis client instance."""
    yield redis_manager.client


__all__ = ["RedisManager", "redis_manager", "get_redis"]
