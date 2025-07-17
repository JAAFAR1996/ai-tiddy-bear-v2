"""Rate limiting state storage management."""

import json
import time

from src.infrastructure.logging_config import get_logger

from .core import RateLimitState

logger = get_logger(__name__, component="security")


class RateLimitStorage:
    """Storage manager for rate limiting state."""

    def __init__(self, redis_client=None):
        self.redis_client = redis_client
        self.local_state: dict[str, RateLimitState] = {}

    async def get_state(self, key: str) -> RateLimitState:
        """Get rate limit state for a key."""
        # Try Redis first if available
        if self.redis_client:
            try:
                data = await self.redis_client.get(f"rate_limit:{key}")
                if data:
                    state_dict = json.loads(data)
                    return RateLimitState(
                        key=key,
                        requests=state_dict.get("requests", []),
                        tokens=state_dict.get("tokens", 0.0),
                        last_refill=state_dict.get("last_refill", time.time()),
                        blocked_until=state_dict.get("blocked_until"),
                        total_requests=state_dict.get("total_requests", 0),
                        first_request=state_dict.get("first_request"),
                    )
            except Exception as e:
                logger.warning(
                    f"Failed to get rate limit state from Redis: {e}"
                )

        # Fallback to local state
        if key not in self.local_state:
            self.local_state[key] = RateLimitState(key=key)
        return self.local_state[key]

    async def save_state(self, key: str, state: RateLimitState) -> None:
        """Save rate limit state for a key."""
        # Save to Redis if available
        if self.redis_client:
            try:
                state_dict = {
                    "requests": state.requests,
                    "tokens": state.tokens,
                    "last_refill": state.last_refill,
                    "blocked_until": state.blocked_until,
                    "total_requests": state.total_requests,
                    "first_request": state.first_request,
                }
                await self.redis_client.set(
                    f"rate_limit:{key}",
                    json.dumps(state_dict),
                    ex=3600,  # Expire after 1 hour
                )
            except Exception as e:
                logger.warning(
                    f"Failed to save rate limit state to Redis: {e}"
                )

        # Always save to local state
        self.local_state[key] = state

    async def cleanup_expired(self) -> None:
        """Clean up expired entries from local state."""
        current_time = time.time()
        expired_keys = [
            key
            for key, state in self.local_state.items()
            if state.blocked_until
            and current_time > state.blocked_until + 3600
        ]
        for key in expired_keys:
            del self.local_state[key]
        logger.info(
            f"Cleaned up {len(expired_keys)} expired rate limit entries."
        )
