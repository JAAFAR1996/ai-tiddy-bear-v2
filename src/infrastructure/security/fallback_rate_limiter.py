"""Fallback Rate Limiter - In-memory sliding window rate limiting."""

import asyncio
import threading
import time
from typing import Any, Optional

from src.infrastructure.logging_config import get_logger

logger = get_logger(__name__)


class SlidingWindowRateLimiter:
    """In-memory sliding window rate limiter."""

    def __init__(self, default_limit: int = 100, window_seconds: int = 60):
        """Initialize the sliding window rate limiter.

        Args:
            default_limit: Default number of requests allowed per window
            window_seconds: Window size in seconds
        """
        self.default_limit = default_limit
        self.window_seconds = window_seconds
        self._user_windows = {}
        self._global_window = []
        self._lock = threading.RLock()
        self._custom_limits = {}
        self._cleanup_interval = 300  # 5 minutes

    async def is_allowed(
        self,
        user_id: str,
        endpoint: Optional[str] = None,
        limit: Optional[int] = None,
        window_seconds: Optional[int] = None,
    ) -> dict[str, Any]:
        """Check if request is allowed within rate limits.

        Args:
            user_id: User identifier
            endpoint: Optional endpoint identifier
            limit: Optional custom limit for this check
            window_seconds: Optional custom window for this check

        Returns:
            Dictionary with rate limit information
        """
        current_time = time.time()
        key = f"{user_id}:{endpoint}" if endpoint else user_id

        # Get rate limit configuration
        rate_limit, window_size = self._get_rate_limit_config(
            user_id, limit, window_seconds, endpoint
        )

        with self._lock:
            # Initialize window for this key if not exists
            if key not in self._user_windows:
                self._user_windows[key] = []

            window = self._user_windows[key]

            # Remove expired requests from window
            cutoff_time = current_time - window_size
            window[:] = [req_time for req_time in window if req_time > cutoff_time]

            # Check if request is allowed
            allowed = len(window) < rate_limit
            remaining = max(0, rate_limit - len(window) - (1 if allowed else 0))

            # Calculate retry_after if blocked
            retry_after = 0
            if not allowed and window:
                retry_after = max(0, window[0] + window_size - current_time)

            # Calculate reset time
            reset_time = current_time + window_size

            # Add current request to window if allowed
            if allowed:
                window.append(current_time)

            result = {
                "allowed": allowed,
                "remaining": remaining,
                "retry_after": retry_after,
                "limit": rate_limit,
                "window_seconds": window_size,
                "reset_time": reset_time,
            }

            logger.debug(f"Rate limit check for {key}: {result}")
            return result

    def _get_rate_limit_config(
        self,
        user_id: str,
        limit: Optional[int],
        window_seconds: Optional[int],
        endpoint: Optional[str] = None,
    ) -> tuple[int, int]:
        """Get rate limit configuration for user/endpoint.

        Returns:
            Tuple of (limit, window_seconds)
        """
        # Method parameters take highest priority
        if limit is not None and window_seconds is not None:
            return limit, window_seconds

        # Check for custom limits
        key = f"{user_id}:{endpoint}" if endpoint else user_id
        if key in self._custom_limits:
            custom_limit, custom_window = self._custom_limits[key]
            return custom_limit, custom_window

        # Fall back to defaults
        return self.default_limit, self.window_seconds

    def set_custom_limit(
        self,
        user_id: str,
        limit: int,
        window_seconds: int,
        endpoint: Optional[str] = None,
    ) -> None:
        """Set custom rate limit for user/endpoint."""
        key = f"{user_id}:{endpoint}" if endpoint else user_id
        with self._lock:
            self._custom_limits[key] = (limit, window_seconds)
        logger.info(f"Set custom rate limit for {key}: {limit}/{window_seconds}s")

    def remove_custom_limit(self, user_id: str, endpoint: Optional[str] = None) -> None:
        """Remove custom rate limit for user/endpoint."""
        key = f"{user_id}:{endpoint}" if endpoint else user_id
        with self._lock:
            self._custom_limits.pop(key, None)
        logger.info(f"Removed custom rate limit for {key}")

    def cleanup_expired_windows(self) -> None:
        """Clean up expired rate limit windows."""
        current_time = time.time()
        with self._lock:
            keys_to_remove = []
            for key, window in self._user_windows.items():
                cutoff_time = current_time - self.window_seconds
                window[:] = [req_time for req_time in window if req_time > cutoff_time]
                if not window:
                    keys_to_remove.append(key)

            for key in keys_to_remove:
                del self._user_windows[key]

        logger.debug(f"Cleaned up {len(keys_to_remove)} expired windows")


class FallbackRateLimitService:
    """Rate limiting service with Redis fallback to in-memory."""

    def __init__(self, redis_client=None):
        """Initialize fallback rate limit service.

        Args:
            redis_client: Optional Redis client for distributed rate limiting
        """
        self.redis_client = redis_client
        self.redis_available = False
        self.fallback_limiter = SlidingWindowRateLimiter()
        self._last_redis_check = 0
        self._redis_check_interval = 30  # Check Redis availability every 30 seconds

    async def check_redis_availability(self) -> bool:
        """Check if Redis is available."""
        if not self.redis_client:
            self.redis_available = False
            return False

        current_time = time.time()

        # Use cached result if recently checked
        if (current_time - self._last_redis_check) < self._redis_check_interval:
            return self.redis_available

        try:
            # Test Redis connection
            await asyncio.to_thread(self.redis_client.ping)
            self.redis_available = True
            logger.debug("Redis is available for rate limiting")
        except Exception as e:
            self.redis_available = False
            logger.warning(f"Redis not available for rate limiting: {e}")

        self._last_redis_check = current_time
        return self.redis_available

    async def is_allowed(
        self,
        user_id: str,
        endpoint: Optional[str] = None,
        limit: Optional[int] = None,
        window_seconds: Optional[int] = None,
    ) -> dict[str, Any]:
        """Check if request is allowed within rate limits.

        Falls back to in-memory rate limiting if Redis is unavailable.

        Args:
            user_id: User identifier
            endpoint: Optional endpoint identifier
            limit: Optional custom limit for this check
            window_seconds: Optional custom window for this check

        Returns:
            Dictionary with rate limit information
        """
        # Check Redis availability
        redis_available = await self.check_redis_availability()

        if redis_available:
            try:
                return await self._redis_rate_limit(
                    user_id, endpoint, limit, window_seconds
                )
            except Exception as e:
                logger.warning(f"Redis rate limiting failed, falling back: {e}")
                # Fall through to in-memory rate limiting

        # Use in-memory fallback
        return await self.fallback_limiter.is_allowed(
            user_id, endpoint, limit, window_seconds
        )

    async def _redis_rate_limit(
        self,
        user_id: str,
        endpoint: Optional[str] = None,
        limit: Optional[int] = None,
        window_seconds: Optional[int] = None,
    ) -> dict[str, Any]:
        """Perform rate limiting using Redis."""
        # This would implement Redis-based sliding window rate limiting
        # For now, fall back to in-memory implementation
        logger.debug("Redis rate limiting not fully implemented, using fallback")
        return await self.fallback_limiter.is_allowed(
            user_id, endpoint, limit, window_seconds
        )

    def set_custom_limit(
        self,
        user_id: str,
        limit: int,
        window_seconds: int,
        endpoint: Optional[str] = None,
    ) -> None:
        """Set custom rate limit for user/endpoint."""
        self.fallback_limiter.set_custom_limit(user_id, limit, window_seconds, endpoint)

    def remove_custom_limit(self, user_id: str, endpoint: Optional[str] = None) -> None:
        """Remove custom rate limit for user/endpoint."""
        self.fallback_limiter.remove_custom_limit(user_id, endpoint)
