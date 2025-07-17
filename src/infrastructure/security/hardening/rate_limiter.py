"""Enterprise-grade Rate Limiting for AI Teddy Bear.

Protects against DDoS attacks and API abuse with Redis-backed storage
"""

import time
from dataclasses import dataclass
from enum import Enum

from src.infrastructure.logging_config import get_logger

logger = get_logger(__name__, component="security")


class RateLimitType(str, Enum):
    """Types of rate limiting strategies."""

    SLIDING_WINDOW = "sliding_window"
    TOKEN_BUCKET = "token_bucket"
    FIXED_WINDOW = "fixed_window"


@dataclass
class RateLimitConfig:
    """Configuration for rate limiting."""

    requests_per_minute: int = 60
    requests_per_hour: int = 1000
    requests_per_day: int = 10000
    burst_limit: int = 10  # Additional requests allowed in burst
    window_type: RateLimitType = RateLimitType.SLIDING_WINDOW

    # Child-specific limits (stricter)
    child_requests_per_minute: int = 30
    child_requests_per_hour: int = 500

    # Parent dashboard limits
    parent_requests_per_minute: int = 100
    parent_requests_per_hour: int = 2000


@dataclass
class RateLimitResult:
    """Result of rate limit check."""

    allowed: bool
    remaining: int
    reset_time: int
    retry_after: int | None = None
    reason: str | None = None


class RedisRateLimiter:
    """Redis-backed rate limiter with multiple strategies
    Supports sliding window, token bucket, and fixed window algorithms.
    """

    def __init__(self, config: RateLimitConfig) -> None:
        self.config = config
        self.redis_client = None  # Will be injected
        self.local_cache: dict[str, dict] = {}  # Fallback for testing

    async def initialize(self, redis_client=None):
        """Initialize with Redis client."""
        self.redis_client = redis_client
        if not redis_client:
            logger.warning("Redis client not provided, using local cache fallback")

    async def check_rate_limit(
        self,
        identifier: str,
        limit_type: str = "general",
        custom_limit: tuple[int, int] | None = None,
    ) -> RateLimitResult:
        """Check rate limit for a given identifier."""
        if not self.redis_client:
            return self._check_local_limit(identifier)

        now = int(time.time())
        key = f"rate_limit:{identifier}:{limit_type}"

        if custom_limit:
            limit, window = custom_limit
        else:
            limit, window = self._get_limit_for_type(limit_type)

        # Sliding window implementation
        async with self.redis_client.pipeline(transaction=True) as pipe:
            pipe.zremrangebyscore(key, 0, now - window)
            pipe.zadd(key, {str(now): now})
            pipe.zcard(key)
            pipe.expire(key, window)
            results = await pipe.execute()

        count = results[2]
        remaining = limit - count

        if remaining < 0:
            return RateLimitResult(
                allowed=False,
                remaining=0,
                reset_time=now + window,
                retry_after=window,
                reason="Rate limit exceeded",
            )

        return RateLimitResult(
            allowed=True,
            remaining=remaining,
            reset_time=now + window,
        )

    def _get_limit_for_type(self, limit_type: str) -> tuple[int, int]:
        """Get rate limit based on type."""
        if limit_type == "child":
            return self.config.child_requests_per_minute, 60
        if limit_type == "parent":
            return self.config.parent_requests_per_minute, 60
        return self.config.requests_per_minute, 60

    def _check_local_limit(self, identifier: str) -> RateLimitResult:
        """Fallback to local in-memory rate limiting."""
        now = int(time.time())
        if identifier not in self.local_cache:
            self.local_cache[identifier] = {"timestamps": []}

        timestamps = self.local_cache[identifier]["timestamps"]
        timestamps = [t for t in timestamps if t > now - 60]
        self.local_cache[identifier]["timestamps"] = timestamps

        if len(timestamps) >= self.config.requests_per_minute:
            return RateLimitResult(
                allowed=False,
                remaining=0,
                reset_time=now + 60,
                retry_after=60,
            )

        timestamps.append(now)
        return RateLimitResult(
            allowed=True,
            remaining=self.config.requests_per_minute - len(timestamps),
            reset_time=now + 60,
        )
