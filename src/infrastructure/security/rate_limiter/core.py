"""Core rate limiting models and enums."""

import time
from dataclasses import dataclass, field
from enum import Enum


class RateLimitType(Enum):
    """Types of rate limiting strategies."""

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
    """Configuration for rate limiting rules."""

    limit_type: RateLimitType
    strategy: RateLimitStrategy
    max_requests: int
    window_seconds: int
    burst_capacity: int | None = None
    refill_rate: float | None = None
    block_duration_seconds: int = 300  # 5 minutes default
    child_safe_mode: bool = True


@dataclass
class RateLimitState:
    """Current state of rate limiting for a key."""

    key: str
    requests: list[float] = field(default_factory=list)
    tokens: float = 0.0
    last_refill: float = field(default_factory=time.time)
    blocked_until: float | None = None
    total_requests: int = 0
    first_request: float | None = None


@dataclass
class RateLimitResult:
    """Result of rate limit check."""

    allowed: bool
    remaining: int
    reset_time: float
    retry_after: int | None = None
    blocked_reason: str | None = None
    child_safety_triggered: bool = False
