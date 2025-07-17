
from collections import defaultdict, deque
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Tuple
import asyncio
import logging
import threading
import time


from src.infrastructure.logging_config import get_logger

logger = get_logger(__name__, component="security")

class SlidingWindowRateLimiter:
   
    def __init__(self, default_limit: int = 100, window_seconds: int = 60) -> None:
        """Initialize rate limiter with default settings."""
        self.default_limit = default_limit
        self.window_seconds = window_seconds
        
        # Thread-safe storage for rate limit windows
        self._user_windows: Dict[str, deque] = defaultdict(deque)
        self._global_window: deque = deque()
        self._lock = threading.RLock()
        
        # Custom limits per user/endpoint
        self._custom_limits: Dict[str, Tuple[int, int]] = {}
        
        # Cleanup tracking
        self._last_cleanup = time.time()
        self._cleanup_interval = 300  # 5 minutes
        
        logger.info(f"Fallback rate limiter initialized: {default_limit} requests per {window_seconds}s")

    async def is_allowed(
        self,
        user_id: str,
        endpoint: Optional[str] = None,
        custom_limit: Optional[int] = None,
        custom_window: Optional[int] = None
    ) -> Dict[str, any]:
        """
        Check if request is allowed under rate limits.
        Args:
            user_id: Unique identifier for the user
            endpoint: Optional endpoint for granular limiting
            custom_limit: Override default rate limit
            custom_window: Override default time window
        Returns:
            Dict with 'allowed', 'remaining', 'reset_time', 'retry_after'
        """
        current_time = time.time()
        key = f"{user_id}:{endpoint}" if endpoint else user_id
        
        # Get rate limit configuration
        limit, window = self._get_rate_limit_config(
            key, custom_limit, custom_window
        )
        
        with self._lock:
            # Cleanup old entries periodically
            if current_time - self._last_cleanup > self._cleanup_interval:
                await self._cleanup_old_entries(current_time)
                self._last_cleanup = current_time
            
            # Get user's request window
            user_window = self._user_windows[key]
            
            # Remove expired requests from window
            cutoff_time = current_time - window
            while user_window and user_window[0] <= cutoff_time:
                user_window.popleft()
            
            # Check if limit exceeded
            current_count = len(user_window)
            if current_count >= limit:
                # Rate limit exceeded
                oldest_request = user_window[0] if user_window else current_time
                reset_time = oldest_request + window
                retry_after = max(0, reset_time - current_time)
                
                logger.warning(f"Rate limit exceeded for {key}: {current_count}/{limit}")
                
                return {
                    "allowed": False,
                    "remaining": 0,
                    "reset_time": datetime.fromtimestamp(reset_time).isoformat(),
                    "retry_after": int(retry_after) + 1,
                    "limit": limit,
                    "window_seconds": window
                }
            
            # Request allowed - add to window
            user_window.append(current_time)
            self._global_window.append(current_time)
            
            # Calculate remaining requests and reset time
            remaining = limit - (current_count + 1)
            reset_time = current_time + window
            
            logger.debug(f"Request allowed for {key}: {current_count + 1}/{limit}")
            
            return {
                "allowed": True,
                "remaining": remaining,
                "reset_time": datetime.fromtimestamp(reset_time).isoformat(),
                "retry_after": 0,
                "limit": limit,
                "window_seconds": window
            }

    def set_custom_limit(
        self,
        user_id: str,
        limit: int,
        window_seconds: Optional[int] = None,
        endpoint: Optional[str] = None
    ) -> None:
        """Set custom rate limit for specific user / endpoint."""
        key = f"{user_id}:{endpoint}" if endpoint else user_id
        window = window_seconds or self.window_seconds
        
        with self._lock:
            self._custom_limits[key] = (limit, window)
        
        logger.info(f"Custom rate limit set for {key}: {limit} requests per {window}s")

    def remove_custom_limit(self, user_id: str, endpoint: Optional[str] = None) -> None:
        """Remove custom rate limit for user / endpoint."""
        key = f"{user_id}:{endpoint}" if endpoint else user_id
        
        with self._lock:
            self._custom_limits.pop(key, None)
        
        logger.info(f"Custom rate limit removed for {key}")

    def _get_rate_limit_config(
        self,
        key: str,
        custom_limit: Optional[int],
        custom_window: Optional[int]
    ) -> Tuple[int, int]:
        """Get rate limit configuration for key."""
        # Priority: method params > stored custom limits > defaults
        if custom_limit is not None:
            return custom_limit, custom_window or self.window_seconds
        
        if key in self._custom_limits:
            return self._custom_limits[key]
        
        return self.default_limit, self.window_seconds

    async def _cleanup_old_entries(self, current_time: float) -> None:
        """Clean up expired entries to prevent memory bloat."""
        cleanup_count = 0
        
        # Clean user windows
        keys_to_remove = []
        for key, window in self._user_windows.items():
            # Get window size for this key
            _, window_seconds = self._get_rate_limit_config(key, None, None)
            cutoff_time = current_time - window_seconds
            
            # Remove expired entries
            while window and window[0] <= cutoff_time:
                window.popleft()
                cleanup_count += 1
            
            # Remove empty windows
            if not window:
                keys_to_remove.append(key)
        
        # Remove empty user windows
        for key in keys_to_remove:
            del self._user_windows[key]
        
        # Clean global window
        global_cutoff = current_time - (self.window_seconds * 2)  # Keep longer for analytics
        while self._global_window and self._global_window[0] <= global_cutoff:
            self._global_window.popleft()
            cleanup_count += 1
        
        if cleanup_count > 0:
            logger.debug(f"Cleaned up {cleanup_count} expired rate limit entries")

    async def get_statistics(self) -> Dict[str, any]:
        """Get rate limiter statistics for monitoring."""
        current_time = time.time()
        
        with self._lock:
            # Calculate active users in last window
            active_users = 0
            total_requests_last_window = 0
            
            for key, window in self._user_windows.items():
                if window:
                    # Count requests in last window
                    _, window_seconds = self._get_rate_limit_config(key, None, None)
                    cutoff_time = current_time - window_seconds
                    recent_requests = sum(1 for req_time in window if req_time > cutoff_time)
                    
                    if recent_requests > 0:
                        active_users += 1
                        total_requests_last_window += recent_requests
            
            # Global statistics
            global_requests_last_hour = sum(
                1 for req_time in self._global_window
                if req_time > current_time - 3600
            )
            
            return {
                "active_users": active_users,
                "total_tracked_users": len(self._user_windows),
                "requests_last_window": total_requests_last_window,
                "requests_last_hour": global_requests_last_hour,
                "custom_limits_count": len(self._custom_limits),
                "memory_usage": {
                    "user_windows": len(self._user_windows),
                    "global_window_size": len(self._global_window),
                    "total_stored_requests": sum(len(w) for w in self._user_windows.values())
                },
                "config": {
                    "default_limit": self.default_limit,
                    "default_window_seconds": self.window_seconds,
                    "cleanup_interval_seconds": self._cleanup_interval
                },
                "last_cleanup": datetime.fromtimestamp(self._last_cleanup).isoformat()
            }

    async def reset_user_limits(self, user_id: str, endpoint: Optional[str] = None) -> bool:
        """Reset rate limits for specific user(admin function)."""
        key = f"{user_id}:{endpoint}" if endpoint else user_id
        
        with self._lock:
            if key in self._user_windows:
                self._user_windows[key].clear()
                logger.info(f"Rate limits reset for {key}")
                return True
            return False

class FallbackRateLimitService:
    """
    High - level rate limiting service with Redis fallback.
    Automatically falls back to in -memory limiting when Redis is unavailable.
    """
    def __init__(self, redis_client=None) -> None:
        """Initialize with optional Redis client."""
        self.redis_client = redis_client
        self.fallback_limiter = SlidingWindowRateLimiter()
        self.redis_available = False
        self.last_redis_check = 0
        self.redis_check_interval = 30  # Check Redis every 30 seconds
        
        logger.info("Fallback rate limit service initialized")

    async def check_redis_availability(self) -> bool:
        """Check if Redis is available for rate limiting."""
        current_time = time.time()
        
        # Don't check too frequently
        if current_time - self.last_redis_check < self.redis_check_interval:
            return self.redis_available
        
        if self.redis_client is None:
            self.redis_available = False
            return False
        
        try:
            # Simple ping to check Redis
            await self.redis_client.ping()
            if not self.redis_available:
                logger.info("Redis connection restored for rate limiting")
            self.redis_available = True
        except Exception as e:
            if self.redis_available:
                logger.warning(f"Redis unavailable, falling back to in-memory rate limiting: {e}")
            self.redis_available = False
        
        self.last_redis_check = current_time
        return self.redis_available

    async def is_allowed(
        self,
        user_id: str,
        endpoint: Optional[str] = None,
        limit: Optional[int] = None,
        window_seconds: Optional[int] = None
    ) -> Dict[str, any]:
        """Check if request is allowed under rate limits."""
        # Try Redis first if available
        if await self.check_redis_availability():
            try:
                return await self._redis_rate_limit(user_id, endpoint, limit, window_seconds)
            except Exception as e:
                logger.error(f"Redis rate limiting failed, using fallback: {e}")
                self.redis_available = False
        
        # Use fallback limiter
        result = await self.fallback_limiter.is_allowed(
            user_id, endpoint, limit, window_seconds
        )
        result["fallback_used"] = True
        return result

    async def _redis_rate_limit(
        self,
        user_id: str,
        endpoint: Optional[str],
        limit: Optional[int],
        window_seconds: Optional[int]
    ) -> Dict[str, any]:
        """Implement Redis - based rate limiting(placeholder)."""
        # This would implement Redis sliding window rate limiting
        # For now, fall back to in-memory
        logger.debug("Redis rate limiting not implemented, using fallback")
        return await self.fallback_limiter.is_allowed(user_id, endpoint, limit, window_seconds)

    async def get_statistics(self) -> Dict[str, any]:
        """Get comprehensive rate limiting statistics."""
        stats = await self.fallback_limiter.get_statistics()
        stats.update({
            "redis_available": self.redis_available,
            "last_redis_check": datetime.fromtimestamp(self.last_redis_check).isoformat(),
            "service_type": "redis" if self.redis_available else "fallback"
        })
        return stats

    def set_custom_limit(
        self,
        user_id: str,
        limit: int,
        window_seconds: Optional[int] = None,
        endpoint: Optional[str] = None
    ) -> None:
        """Set custom rate limit(applies to fallback, Redis limits handled separately)."""
        self.fallback_limiter.set_custom_limit(user_id, limit, window_seconds, endpoint)

    async def reset_user_limits(self, user_id: str, endpoint: Optional[str] = None) -> bool:
        """Reset rate limits for user across all systems."""
        # Reset fallback limits
        fallback_reset = await self.fallback_limiter.reset_user_limits(user_id, endpoint)

        # Reset Redis limits if available
        redis_reset = True
        if hasattr(self, '_redis_client') and self._redis_client:
            try:
                # Reset Redis rate limiting keys
                redis_key = f"rate_limit:{user_id}:{endpoint}"
                await self._redis_client.delete(redis_key)
                redis_reset = True
            except Exception as e:
                logger.warning(f"Failed to reset Redis rate limits for {user_id}: {e}")
                redis_reset = False
        
        return fallback_reset or redis_reset