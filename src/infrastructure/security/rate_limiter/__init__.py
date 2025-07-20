"""Modular rate limiting system for AI Teddy Bear backend.

This package provides a comprehensive rate limiting solution with:
- Multiple rate limiting strategies (fixed window, sliding window, token bucket)
- Child safety specific configurations
- Redis-backed persistence with local fallback
- Comprehensive audit logging
"""

from .convenience import (
    check_api_rate_limit,
    check_auth_rate_limit,
    check_child_interaction_limit,
)
from .core import (
    RateLimitConfig,
    RateLimitResult,
    RateLimitState,
    RateLimitStrategy,
    RateLimitType,
)
from .service import ComprehensiveRateLimiter, get_rate_limiter

__all__ = [
    "ComprehensiveRateLimiter",
    "RateLimitConfig",
    "RateLimitResult",
    "RateLimitState",
    "RateLimitStrategy",
    "RateLimitType",
    "check_api_rate_limit",
    "check_auth_rate_limit",
    "check_child_interaction_limit",
    "get_rate_limiter",
]
