"""Convenience functions for common rate limiting scenarios."""

from .core import RateLimitResult
from .service import get_rate_limiter


async def check_child_interaction_limit(
    child_id: str,
    user_id: str | None = None,
    ip_address: str | None = None,
) -> RateLimitResult:
    """Check child interaction rate limits."""
    limiter = get_rate_limiter()
    return await limiter.check_rate_limit(
        key=child_id,
        config_name="child_interaction",
        user_id=user_id,
        child_id=child_id,
        ip_address=ip_address,
    )


async def check_auth_rate_limit(
    identifier: str,
    ip_address: str | None = None,
) -> RateLimitResult:
    """Check authentication rate limits."""
    limiter = get_rate_limiter()
    return await limiter.check_rate_limit(
        key=identifier,
        config_name="auth_login",
        ip_address=ip_address,
    )


async def check_api_rate_limit(
    key: str,
    user_id: str | None = None,
    ip_address: str | None = None,
) -> RateLimitResult:
    """Check general API rate limits."""
    limiter = get_rate_limiter()
    return await limiter.check_rate_limit(
        key=key,
        config_name="api_general",
        user_id=user_id,
        ip_address=ip_address,
    )
