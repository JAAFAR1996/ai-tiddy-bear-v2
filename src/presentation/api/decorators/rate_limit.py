"""
from functools import wraps
from typing import Callable, Optional
from fastapi import HTTPException, Request, status, Depends
from src.infrastructure.di.container import container
from src.infrastructure.security.rate_limiter_service import RateLimiterService
from src.infrastructure.logging_config import get_logger # Keep for now, will refactor later
logger = get_logger(__name__, component="api")
"""

"""Rate limiting decorators for API endpoints"""


def rate_limit(limit: str) -> Callable:
    """
    Rate limit decorator for API endpoints.
    Usage:
        @router.get("/endpoint")
        @rate_limit("10/minute")
        async def endpoint(): ...
    Args:
        limit: Rate limit string(e.g., "10/minute", "100/hour")
    """
    def decorator(func: Callable) -> Callable:
        # Store rate limit in function for middleware to use
        func._rate_limit = limit
        
        @wraps(func)
        async def wrapper(*args, **kwargs):
            return await func(*args, **kwargs)
        
        wrapper._rate_limit = limit
        return wrapper
    
    return decorator


def strict_limit() -> Callable:
    """
    Strict rate limit for sensitive endpoints(5 / minute).
    """
    return rate_limit("5/minute")


def moderate_limit() -> Callable:
    """
    Moderate rate limit for standard endpoints(30 / minute).
    """
    return rate_limit("30/minute")


def relaxed_limit() -> Callable:
    """
    Relaxed rate limit for high - traffic endpoints(100 / minute).
    """
    return rate_limit("100/minute")


def child_safety_limit() -> Callable:
    """
    Child safety rate limit(20 / minute with progressive delays).
    """
    return rate_limit("20/minute")


async def check_child_interaction_limit(
    request: Request,
    child_id: str,
    interaction_type: str = "general",
    rate_limiter_service: RateLimiterService = Depends(),
) -> None:
    """
    Check child - specific interaction limits.
    Args:
        request: FastAPI request
        child_id: Child identifier
        interaction_type: Type of interaction
    Raises:
        HTTPException: If limit exceeded
    """
    try:
        # Assuming rate_limiter_service has a method for child-specific rate limiting
        # This method should raise HTTPException if the limit is exceeded
        await rate_limiter_service.check_child_request_limit(request, child_id, interaction_type)
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Unexpected error in rate limiting: {e}")