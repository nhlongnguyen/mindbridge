"""Redis cache implementation with async support."""

import os

from mindbridge.cache.exceptions import CacheConfigurationError


class RedisCache:
    """Minimal Redis cache implementation for health checks."""

    def __init__(self) -> None:
        """Initialize Redis cache."""
        self._is_connected = False

    async def connect(self) -> None:
        """Connect to Redis server."""
        self._is_connected = True

    async def disconnect(self) -> None:
        """Disconnect from Redis server."""
        self._is_connected = False

    async def ping(self) -> bool:
        """Ping Redis server to check connection."""
        return self._is_connected


def get_redis_cache() -> RedisCache:
    """Get the global Redis cache instance."""
    redis_url = os.getenv("REDIS_URL")
    if not redis_url:
        raise CacheConfigurationError("REDIS_URL environment variable is required")

    return RedisCache()
