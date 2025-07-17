"""Comprehensive Rate Limiting Service for Child Safety and Security.
This module provides backwards compatibility imports from the new modular rate limiting system.
The implementation has been refactored into smaller, more maintainable modules.
"""

from src.infrastructure.logging_config import get_logger

from .rate_limiter import (
    ComprehensiveRateLimiter,
    RateLimitConfig,
    RateLimitResult,
    RateLimitState,
    RateLimitStrategy,
    RateLimitType,
    check_api_rate_limit,
    check_auth_rate_limit,
    check_child_interaction_limit,
    get_rate_limiter,
)

logger = get_logger(__name__, component="security")

# Export all the imported components for backwards compatibility
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
