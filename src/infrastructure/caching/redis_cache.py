"""Redis cache manager - main caching interface"""

import redis.asyncio as redis

from src.infrastructure.logging_config import get_logger

from .cache_config import CacheConfig
from .strategies.invalidation_strategy import CacheInvalidationStrategy

logger = get_logger(__name__, component="infrastructure")


class RedisCacheManager:
    """Production Redis cache manager with child safety features."""

    def __init__(self, redis_url: str = "redis://localhost:6379/0") -> None:
        self.redis_url = redis_url
        self.redis_client: redis.Redis | None = None
        self.config = CacheConfig()
        self.invalidation_strategy: CacheInvalidationStrategy | None = None
        self._initialized = False

    async def initialize(self) -> None:
        """Initialize Redis connection."""
        if self._initialized:
            return
        try:
            self.redis_client = redis.from_url(
                self.redis_url,
                encoding="utf-8",
                decode_responses=True,
                socket_keepalive=True,
                socket_keepalive_options={
                    1: 1,  # TCP_KEEPIDLE
                    2: 2,  # TCP_KEEPINTVL
                    3: 5,  # TCP_KEEPCNT
                },
            )
            # Test connection
            await self.redis_client.ping()
            # Initialize invalidation strategy
            self.invalidation_strategy = CacheInvalidationStrategy(self.redis_client)
            self._initialized = True
            logger.info("Redis cache manager initialized successfully")
        except Exception as e:
            logger.error(f"Failed to initialize Redis: {e}")
            raise

    async def close(self) -> None:
        """Close Redis connection."""
        if self.redis_client:
            await self.redis_client.close()
            self._initialized = False
            logger.info("Redis connection closed")


def get_cache_manager() -> RedisCacheManager:
    """Get cache manager instance."""
    return RedisCacheManager()
