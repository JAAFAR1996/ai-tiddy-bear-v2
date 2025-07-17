"""
Advanced rate limiting for child safety and system protection.

Implements 2025 slowapi patterns with child-specific controls.
"""
import logging
from collections import defaultdict
from datetime import datetime, timedelta
from typing import Any, Callable, Dict

from fastapi import Depends, FastAPI, HTTPException, Request, status
from fastapi.responses import JSONResponse

from src.infrastructure.config.settings import Settings, get_settings
from src.infrastructure.logging_config import get_logger

logger = get_logger(__name__, component="security")

# Graceful imports for external dependencies
try:
    from slowapi import Limiter
    from slowapi.errors import RateLimitExceeded
    from slowapi.util import get_remote_address

    SLOWAPI_AVAILABLE = True
except (ImportError, UnicodeDecodeError) as e:
    logger.warning(
        f"slowapi not available or config error: {e}, using mock implementation"
    )
    SLOWAPI_AVAILABLE = False

    class Limiter:
        def __init__(self, *args, **kwargs) -> None:
            pass

        def limit(self, *args, **kwargs) -> Callable:
            def decorator(func) -> Callable:
                return func

            return decorator

    def get_remote_address(request):
        return "127.0.0.1"

    class RateLimitExceeded(Exception):
        pass


try:
    from fastapi import FastAPI, HTTPException, Request, status
    from fastapi.responses import JSONResponse

    FASTAPI_AVAILABLE = True
except ImportError:
    logger.warning("fastapi not available, using mock implementation")
    FASTAPI_AVAILABLE = False

    class Request:
        pass

    class HTTPException(Exception):
        def __init__(self, status_code: int, detail: str) -> None:
            self.status_code = status_code
            self.detail = detail

    class status:
        HTTP_429_TOO_MANY_REQUESTS = 429

    class JSONResponse:
        def __init__(self, content: dict, status_code: int) -> None:
            self.content = content
            self.status_code = status_code

    class FastAPI:
        pass


class ChildSafetyRateLimiter:
    """
    Advanced rate limiter with child-specific safety controls.
    Implements dynamic rate limits based on user behavior and child safety context.
    """

    def __init__(self, settings: Settings = Depends(get_settings)) -> None:
        self.settings = settings
        self.limiter = Limiter(
            key_func=get_remote_address,
            default_limits=[self.settings.security.DEFAULT_RATE_LIMIT],
            storage_uri=self.settings.security.REDIS_URL_RATE_LIMIT,
        )
        # Child-specific limits
        self.child_interaction_limits = defaultdict(list)
        self.child_lockout_period = timedelta(
            seconds=self.settings.security.CHILD_LOCKOUT_SECONDS
        )
        self.max_child_interactions = (
            self.settings.security.CHILD_MAX_INTERACTIONS_PER_MINUTE
        )

    def get_limiter(self) -> Limiter:
        return self.limiter

    async def check_child_interaction(self, child_id: str, request: Request) -> None:
        """
        Rate limit child interactions to prevent abuse and ensure safety.
        """
        now = datetime.utcnow()
        # Clean up old interactions
        self.child_interaction_limits[child_id] = [
            t for t in self.child_interaction_limits[child_id] if now - t < timedelta(minutes=1)
        ]

        # Check if limit exceeded
        if len(self.child_interaction_limits[child_id]) >= self.max_child_interactions:
            logger.warning(
                f"Child interaction limit exceeded for child_id: {child_id}"
            )
            raise HTTPException(
                status_code=status.HTTP_429_TOO_MANY_REQUESTS,
                detail="Interaction limit reached. Please try again later.",
            )

        # Record interaction
        self.child_interaction_limits[child_id].append(now)

    def register_rate_limit_handler(self, app: FastAPI) -> None:
        """
        Register the rate limit exceeded handler with the FastAPI app.
        """

        @app.exception_handler(RateLimitExceeded)
        async def rate_limit_exceeded_handler(
            request: Request, exc: RateLimitExceeded
        ) -> JSONResponse:
            logger.warning(
                f"Rate limit exceeded for {request.url.path}: {exc.detail}"
            )
            return JSONResponse(
                status_code=status.HTTP_429_TOO_MANY_REQUESTS,
                content={"detail": f"Rate limit exceeded: {exc.detail}"},
            )


_rate_limiter_instance = None


def get_child_safety_rate_limiter(
    settings: Settings = Depends(get_settings),
) -> ChildSafetyRateLimiter:
    global _rate_limiter_instance
    if _rate_limiter_instance is None:
        _rate_limiter_instance = ChildSafetyRateLimiter(settings)
    return _rate_limiter_instance