"""Advanced rate limiting for child safety and system protection.

Implements 2025 slowapi patterns with child-specific controls.
"""

from collections import defaultdict
from collections.abc import Callable
from datetime import datetime, timedelta

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
        f"slowapi not available or config error: {e}, using mock implementation",
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
    from fastapi import Depends, FastAPI, HTTPException, Request, status
    from fastapi.responses import JSONResponse

    FASTAPI_AVAILABLE = True
except ImportError:
    logger.warning("fastapi not available, using mock implementation")
    FASTAPI_AVAILABLE = False

    class Depends:
        def __init__(self, dependency):
            self.dependency = dependency

    class Request:
        def __init__(self):
            self.url = type("URL", (), {"path": "/"})()

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
        def exception_handler(self, exc_class):
            def decorator(func):
                return func

            return decorator


class ChildSafetyLimiter:
    """Advanced rate limiter with child-specific safety controls.
    Implements dynamic rate limits based on user behavior and child safety context.
    """

    def __init__(self, settings: Settings = None) -> None:
        if settings is None:
            settings = get_settings()

        self.settings = settings

        if SLOWAPI_AVAILABLE:
            self.limiter = Limiter(
                key_func=get_remote_address,
                default_limits=[self.settings.security.DEFAULT_RATE_LIMIT],
                storage_uri=getattr(
                    self.settings.security, "REDIS_URL_RATE_LIMIT", "memory://"
                ),
            )
        else:
            self.limiter = Limiter()

        # Child-specific limits
        self.child_interaction_limits = defaultdict(list)
        self.child_lockout_period = timedelta(
            seconds=getattr(
                self.settings.security,
                "CHILD_LOCKOUT_SECONDS",
                300,  # 5 minutes default
            )
        )
        self.max_child_interactions = getattr(
            self.settings.security,
            "CHILD_MAX_INTERACTIONS_PER_MINUTE",
            10,  # 10 interactions per minute default
        )

    def get_limiter(self) -> Limiter:
        """Get the rate limiter instance"""
        return self.limiter

    async def check_child_interaction(
        self, child_id: str, request: Request = None
    ) -> None:
        """Rate limit child interactions to prevent abuse and ensure safety."""
        now = datetime.utcnow()

        # Clean up old interactions
        self.child_interaction_limits[child_id] = [
            t
            for t in self.child_interaction_limits[child_id]
            if now - t < timedelta(minutes=1)
        ]

        # Check if limit exceeded
        if len(self.child_interaction_limits[child_id]) >= self.max_child_interactions:
            logger.warning(f"Child interaction limit exceeded for child_id: {child_id}")
            raise HTTPException(
                status_code=status.HTTP_429_TOO_MANY_REQUESTS,
                detail="Interaction limit reached. Please try again later.",
            )

        # Record interaction
        self.child_interaction_limits[child_id].append(now)

    def is_child_locked_out(self, child_id: str) -> bool:
        """Check if a child is currently locked out"""
        if child_id not in self.child_interaction_limits:
            return False

        now = datetime.utcnow()
        recent_interactions = [
            t
            for t in self.child_interaction_limits[child_id]
            if now - t < self.child_lockout_period
        ]

        return len(recent_interactions) >= self.max_child_interactions

    def get_child_interaction_count(self, child_id: str) -> int:
        """Get current interaction count for a child"""
        now = datetime.utcnow()
        self.child_interaction_limits[child_id] = [
            t
            for t in self.child_interaction_limits[child_id]
            if now - t < timedelta(minutes=1)
        ]
        return len(self.child_interaction_limits[child_id])

    def reset_child_interactions(self, child_id: str) -> None:
        """Reset interaction count for a child (admin function)"""
        if child_id in self.child_interaction_limits:
            del self.child_interaction_limits[child_id]
        logger.info(f"Reset interaction limits for child_id: {child_id}")

    def register_rate_limit_handler(self, app) -> None:
        """Register the rate limit exceeded handler with the FastAPI app."""
        if not FASTAPI_AVAILABLE:
            logger.warning(
                "FastAPI not available, skipping rate limit handler registration"
            )
            return

        @app.exception_handler(RateLimitExceeded)
        async def rate_limit_exceeded_handler(
            request: Request,
            exc: RateLimitExceeded,
        ) -> JSONResponse:
            logger.warning(f"Rate limit exceeded for {request.url.path}: {exc.detail}")
            return JSONResponse(
                status_code=status.HTTP_429_TOO_MANY_REQUESTS,
                content={
                    "detail": f"Rate limit exceeded: {exc.detail}",
                    "retry_after": 60,  # Suggest retry after 60 seconds
                    "message": "Please wait before making more requests.",
                },
            )

    def get_rate_limit_status(self, child_id: str = None) -> dict:
        """Get current rate limiting status"""
        status_info = {
            "slowapi_available": SLOWAPI_AVAILABLE,
            "fastapi_available": FASTAPI_AVAILABLE,
            "max_child_interactions": self.max_child_interactions,
            "lockout_period_seconds": self.child_lockout_period.total_seconds(),
        }

        if child_id:
            status_info.update(
                {
                    "child_id": child_id,
                    "current_interactions": self.get_child_interaction_count(child_id),
                    "is_locked_out": self.is_child_locked_out(child_id),
                }
            )

        return status_info


# Global instance management
_rate_limiter_instance = None


def get_child_safety_rate_limiter(
    settings: Settings = None,
) -> ChildSafetyRateLimiter:
    """Get or create the global rate limiter instance"""
    global _rate_limiter_instance
    if _rate_limiter_instance is None:
        if settings is None:
            settings = get_settings()
        _rate_limiter_instance = ChildSafetyRateLimiter(settings)
    return _rate_limiter_instance


def create_rate_limiter_dependency():
    """Create a FastAPI dependency for the rate limiter"""
    if FASTAPI_AVAILABLE:
        return Depends(get_child_safety_rate_limiter)
    return get_child_safety_rate_limiter


# Convenience functions for easy use
def check_child_rate_limit(child_id: str, request: Request = None):
    """Convenience function to check child rate limits"""
    limiter = get_child_safety_rate_limiter()
    return limiter.check_child_interaction(child_id, request)


def get_rate_limit_status(child_id: str = None) -> dict:
    """Convenience function to get rate limit status"""
    limiter = get_child_safety_rate_limiter()
    return limiter.get_rate_limit_status(child_id)
