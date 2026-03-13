"""
Redis client for caching and background jobs.
"""
import redis.asyncio as aioredis
from typing import Optional

from ..config import settings


class RedisClient:
    """Redis client singleton."""

    _instance: Optional["RedisClient"] = None
    _cache_client: Optional[aioredis.Redis] = None
    _jobs_client: Optional[aioredis.Redis] = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance

    async def init_cache(self) -> None:
        """Initialize cache Redis client."""
        self._cache_client = await aioredis.from_url(
            settings.REDIS_CACHE_URL,
            encoding="utf-8",
            decode_responses=True,
        )

    async def init_jobs(self) -> None:
        """Initialize jobs Redis client."""
        self._jobs_client = await aioredis.from_url(
            settings.REDIS_JOBS_URL,
            encoding="utf-8",
            decode_responses=True,
        )

    @property
    def cache(self) -> aioredis.Redis:
        """Get cache Redis client."""
        if self._cache_client is None:
            raise RuntimeError("Cache client not initialized. Call init_cache() first.")
        return self._cache_client

    @property
    def jobs(self) -> aioredis.Redis:
        """Get jobs Redis client."""
        if self._jobs_client is None:
            raise RuntimeError("Jobs client not initialized. Call init_jobs() first.")
        return self._jobs_client

    async def close(self) -> None:
        """Close Redis connections."""
        if self._cache_client:
            await self._cache_client.close()
        if self._jobs_client:
            await self._jobs_client.close()


redis_client = RedisClient()
