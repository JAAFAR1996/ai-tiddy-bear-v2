"""Cache invalidation strategy."""

import redis.asyncio as redis

from src.infrastructure.logging_config import get_logger

from ..cache_config import CacheConfig

logger = get_logger(__name__, component="infrastructure")


class CacheInvalidationStrategy:
    """Manages cache invalidation patterns and strategies."""

    def __init__(self, redis_client: redis.Redis) -> None:
        self.redis_client = redis_client
        self.config = CacheConfig()

    async def invalidate_pattern(self, pattern: str) -> int:
        """Invalidate all keys matching pattern."""
        try:
            # Use SCAN to find keys (better than KEYS for production)
            keys_to_delete = []
            async for key in self.redis_client.scan_iter(match=pattern, count=100):
                keys_to_delete.append(key)
            if keys_to_delete:
                deleted = await self.redis_client.delete(*keys_to_delete)
                logger.info(f"Invalidated {deleted} keys matching pattern: {pattern}")
                return deleted
            return 0
        except Exception as e:
            logger.error(f"Error invalidating cache pattern {pattern}: {e}")
            return 0

    async def invalidate_by_event(self, event_type: str) -> int:
        """Invalidate cache based on event type."""
        patterns = self.config.INVALIDATION_PATTERNS.get(event_type, [])
        if not patterns:
            logger.warning(f"No invalidation patterns defined for event: {event_type}")
            return 0
        total_deleted = 0
        for pattern in patterns:
            deleted = await self.invalidate_pattern(pattern)
            total_deleted += deleted
        logger.info(f"Invalidated {total_deleted} keys for event: {event_type}")
        return total_deleted

    async def invalidate_child_data(self, child_id: str) -> int:
        """Invalidate all cache entries for a specific child."""
        patterns = [
            f"{self.config.CHILD_PREFIX}{child_id}*",
            f"{self.config.SAFETY_PREFIX}{child_id}*",
            f"{self.config.AI_RESPONSE_PREFIX}{child_id}*",
        ]
        total_deleted = 0
        for pattern in patterns:
            deleted = await self.invalidate_pattern(pattern)
            total_deleted += deleted
        return total_deleted

    async def invalidate_user_session(self, user_id: str) -> int:
        """Invalidate user session data."""
        pattern = f"{self.config.SESSION_PREFIX}{user_id}*"
        return await self.invalidate_pattern(pattern)

    async def clear_expired(self) -> int:
        """Clear expired entries(Redis handles this automatically with TTL)."""
        # This is a placeholder - Redis automatically removes expired keys
        # But we can use this for custom expiration logic if needed
        logger.debug("Redis handles expiration automatically via TTL")
        return 0
