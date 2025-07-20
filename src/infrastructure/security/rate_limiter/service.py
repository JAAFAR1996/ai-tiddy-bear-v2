"""Main rate limiting service implementation."""

import asyncio
import time
from typing import Any

from src.infrastructure.logging_config import get_logger
from src.infrastructure.security.comprehensive_audit_integration import (
    get_audit_integration,
)

from .child_safety import ChildSafetyHandler
from .config import DefaultConfigurations
from .core import RateLimitConfig, RateLimitResult
from .storage import RateLimitStorage
from .strategies import RateLimitingStrategies

logger = get_logger(__name__, component="security")


class ComprehensiveRateLimiter:
    """Comprehensive rate limiting service with multiple strategies and child safety features.

    Features:
    - Multiple rate limiting strategies (fixed window, sliding window, token bucket)
    - Child-specific rate limits for safety
    - Authentication attempt protection
    - API endpoint protection
    - Automatic blocking for suspicious activity
    - Comprehensive audit logging
    - Redis-backed persistence (optional)
    """

    def __init__(self, redis_client=None):
        self.storage = RateLimitStorage(redis_client)
        self.configs: dict[str, RateLimitConfig] = (
            DefaultConfigurations.get_default_configs()
        )
        self.child_safety_handler = ChildSafetyHandler()
        self.audit_integration = get_audit_integration()
        # Start cleanup task
        asyncio.create_task(self._cleanup_expired_entries())

    async def check_rate_limit(
        self,
        key: str,
        config_name: str,
        user_id: str | None = None,
        child_id: str | None = None,
        ip_address: str | None = None,
        request_details: dict[str, Any] | None = None,
    ) -> RateLimitResult:
        """Check if request is within rate limits.

        Args:
            key: Unique identifier for rate limiting (e.g., user_id, ip_address)
            config_name: Name of rate limit configuration to use
            user_id: User ID for audit logging
            child_id: Child ID for audit logging
            ip_address: IP address for audit logging
            request_details: Additional details about the request

        Returns:
            RateLimitResult indicating if request is allowed

        """
        config = self.configs.get(config_name)
        if not config:
            raise ValueError(f"Rate limit configuration '{config_name}' not found")

        state = await self.storage.get_state(key)

        # Check if key is currently blocked
        if state.blocked_until and time.time() < state.blocked_until:
            return RateLimitResult(
                allowed=False,
                remaining=0,
                reset_time=state.blocked_until,
                retry_after=int(state.blocked_until - time.time()),
                blocked_reason="blocked",
            )

        # Apply rate limiting strategy
        result = await RateLimitingStrategies.apply_strategy(config, state)

        # Handle rate limit violation
        if not result.allowed:
            # Block key if necessary
            if self.child_safety_handler.should_block_key(config, state):
                state.blocked_until = time.time() + config.block_duration_seconds
                result.retry_after = config.block_duration_seconds
                result.blocked_reason = "blocked_due_to_suspicious_activity"

            # Trigger child safety violation if applicable
            if config.child_safe_mode:
                await self.child_safety_handler.handle_child_safety_violation(
                    config,
                    key,
                    user_id,
                    child_id,
                    ip_address,
                )
                result.child_safety_triggered = True

        # Log and audit the request
        await self.audit_integration.log_rate_limit_event(
            key=key,
            config_name=config_name,
            result=result,
            user_id=user_id,
            child_id=child_id,
            ip_address=ip_address,
        )

        # Save updated state
        await self.storage.save_state(key, state)
        return result

    async def _cleanup_expired_entries(self):
        """Periodically clean up expired rate limit entries."""
        while True:
            await asyncio.sleep(3600)  # Run every hour
            await self.storage.cleanup_expired()


_rate_limiter_instance = None


def get_rate_limiter(redis_client=None) -> ComprehensiveRateLimiter:
    """Get singleton instance of the rate limiter."""
    global _rate_limiter_instance
    if _rate_limiter_instance is None:
        _rate_limiter_instance = ComprehensiveRateLimiter(redis_client)
    return _rate_limiter_instance
