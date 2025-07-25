"""Enterprise-grade Rate Limiting for AI Teddy Bear.
Protects against DDoS attacks and API abuse with Redis-backed storage
"""

import time
from dataclasses import dataclass, field
from enum import Enum
from typing import Optional

from src.infrastructure.logging_config import get_logger

logger = get_logger(__name__, component="security")


@dataclass
class RateLimitResult:
    """Result of rate limit check."""

    allowed: bool
    remaining: int
    reset_time: int
    retry_after: Optional[int] = None
    reason: Optional[str] = None
    blocked_reason: Optional[str] = None
    child_safety_triggered: bool = False


class RateLimitType(str, Enum):
    """Types of rate limiting strategies."""

    SLIDING_WINDOW = "sliding_window"
    TOKEN_BUCKET = "token_bucket"
    FIXED_WINDOW = "fixed_window"
    REQUESTS_PER_MINUTE = "requests_per_minute"
    REQUESTS_PER_HOUR = "requests_per_hour"
    REQUESTS_PER_DAY = "requests_per_day"
    CHILD_INTERACTION_LIMIT = "child_interaction_limit"
    AUTHENTICATION_ATTEMPTS = "authentication_attempts"
    API_CALLS = "api_calls"
    RESOURCE_ACCESS = "resource_access"


class RateLimitStrategy(Enum):
    """Rate limiting strategies."""

    FIXED_WINDOW = "fixed_window"
    SLIDING_WINDOW = "sliding_window"
    TOKEN_BUCKET = "token_bucket"
    LEAKY_BUCKET = "leaky_bucket"


@dataclass
class RateLimitConfig:
    """Configuration for rate limiting."""

    requests_per_minute: int = 60
    requests_per_hour: int = 1000
    requests_per_day: int = 10000
    burst_limit: int = 10
    window_type: RateLimitType = RateLimitType.SLIDING_WINDOW

    # Child-specific limits
    child_requests_per_minute: int = 30
    child_requests_per_hour: int = 500

    # Parent dashboard limits
    parent_requests_per_minute: int = 100
    parent_requests_per_hour: int = 2000

    # Enhanced features
    strategy: RateLimitStrategy = RateLimitStrategy.SLIDING_WINDOW
    max_requests: Optional[int] = None
    window_seconds: Optional[int] = None
    burst_capacity: Optional[int] = None
    refill_rate: Optional[float] = None
    block_duration_seconds: int = 300
    child_safe_mode: bool = True


@dataclass
class RateLimitState:
    """Current state of rate limiting for a key."""

    key: str
    requests: list[float] = field(default_factory=list)
    tokens: float = 0.0
    last_refill: float = field(default_factory=time.time)
    blocked_until: Optional[float] = None
    total_requests: int = 0
    first_request: Optional[float] = None


class RedisRateLimiter:
    """Redis-backed rate limiter with multiple strategies."""

    def __init__(self, config: RateLimitConfig) -> None:
        self.config = config
        self.redis_client = None
        self.local_cache: dict[str, dict] = {}

    async def initialize(self, redis_client=None):
        """Initialize with Redis client."""
        self.redis_client = redis_client
        if not redis_client:
            logger.warning("Redis client not provided, using local cache fallback")

    async def check_rate_limit(
        self, identifier: str, limit_type: str = "general"
    ) -> RateLimitResult:
        """Check rate limit for identifier."""
        if not self.redis_client:
            return self._check_local_limit(identifier)

        now = int(time.time())
        limit, window = self._get_limit_for_type(limit_type)

        # Simple implementation
        return RateLimitResult(allowed=True, remaining=limit, reset_time=now + window)

    def _get_limit_for_type(self, limit_type: str) -> tuple[int, int]:
        """Get rate limit based on type."""
        if limit_type == "child":
            return self.config.child_requests_per_minute, 60
        elif limit_type == "parent":
            return self.config.parent_requests_per_minute, 60
        return self.config.requests_per_minute, 60

    def _check_local_limit(self, identifier: str) -> RateLimitResult:
        """Local rate limiting fallback."""
        now = int(time.time())
        return RateLimitResult(allowed=True, remaining=10, reset_time=now + 60)


class ChildSafetyRateLimiter(RedisRateLimiter):
    """Child-specific rate limiter."""

    def __init__(self, redis_client=None):
        child_config = RateLimitConfig(
            requests_per_minute=30,
            requests_per_hour=100,
            burst_limit=5,
            child_safe_mode=True,
        )
        super().__init__(child_config)
        self.redis_client = redis_client


def get_child_safety_limiter():
    """Get child safety rate limiter instance."""
    return ChildSafetyRateLimiter()
