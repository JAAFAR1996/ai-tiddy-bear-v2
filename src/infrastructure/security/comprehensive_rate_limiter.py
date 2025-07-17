"""Comprehensive Rate Limiting Service for Child Safety and Security.
This module provides backwards compatibility imports from the new modular rate limiting system.
The implementation has been refactored into smaller, more maintainable modules."""

import logging
from .rate_limiter import (
    RateLimitType,
    RateLimitStrategy,
    RateLimitConfig,
    RateLimitState,
    RateLimitResult,
    ComprehensiveRateLimiter,
    get_rate_limiter,
    check_child_interaction_limit,
    check_auth_rate_limit,
    check_api_rate_limit)

from src.infrastructure.logging_config import get_logger
logger = get_logger(__name__, component="security")

# Export all the imported components for backwards compatibility
__all__ = [
    "RateLimitType",
    "RateLimitStrategy",
    "RateLimitConfig",
    "RateLimitState",
    "RateLimitResult",
    "ComprehensiveRateLimiter",
    "get_rate_limiter",
    "check_child_interaction_limit",
    "check_auth_rate_limit",
    "check_api_rate_limit"
]