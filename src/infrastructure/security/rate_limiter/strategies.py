"""Rate limiting strategy implementations."""

import time

from .core import RateLimitConfig, RateLimitResult, RateLimitState, RateLimitStrategy


class RateLimitingStrategies:
    """Implementation of various rate limiting strategies."""

    @staticmethod
    async def apply_strategy(
        config: RateLimitConfig,
        state: RateLimitState,
    ) -> RateLimitResult:
        """Apply the configured rate limiting strategy."""
        current_time = time.time()
        if config.strategy == RateLimitStrategy.FIXED_WINDOW:
            return await RateLimitingStrategies._apply_fixed_window(
                config,
                state,
                current_time,
            )
        if config.strategy == RateLimitStrategy.SLIDING_WINDOW:
            return await RateLimitingStrategies._apply_sliding_window(
                config,
                state,
                current_time,
            )
        if config.strategy == RateLimitStrategy.TOKEN_BUCKET:
            return await RateLimitingStrategies._apply_token_bucket(
                config,
                state,
                current_time,
            )
        # Default to sliding window
        return await RateLimitingStrategies._apply_sliding_window(
            config,
            state,
            current_time,
        )

    @staticmethod
    async def _apply_fixed_window(
        config: RateLimitConfig,
        state: RateLimitState,
        current_time: float,
    ) -> RateLimitResult:
        """Apply fixed window rate limiting."""
        # Calculate window start
        window_start = int(current_time / config.window_seconds) * config.window_seconds

        # Reset counter if we're in a new window
        if not state.first_request or state.first_request < window_start:
            state.requests = []
            state.total_requests = 0
            state.first_request = current_time

        # Count requests in current window
        current_requests = len([r for r in state.requests if r >= window_start])

        if current_requests >= config.max_requests:
            reset_time = window_start + config.window_seconds
            return RateLimitResult(
                allowed=False,
                remaining=0,
                reset_time=reset_time,
                retry_after=int(reset_time - current_time),
            )
        state.requests.append(current_time)
        state.total_requests += 1
        return RateLimitResult(
            allowed=True,
            remaining=config.max_requests - current_requests - 1,
            reset_time=window_start + config.window_seconds,
        )

    @staticmethod
    async def _apply_sliding_window(
        config: RateLimitConfig,
        state: RateLimitState,
        current_time: float,
    ) -> RateLimitResult:
        """Apply sliding window rate limiting."""
        # Remove requests outside the window
        window_start = current_time - config.window_seconds
        state.requests = [r for r in state.requests if r > window_start]

        if len(state.requests) >= config.max_requests:
            reset_time = state.requests[0] + config.window_seconds
            return RateLimitResult(
                allowed=False,
                remaining=0,
                reset_time=reset_time,
                retry_after=int(reset_time - current_time),
            )
        state.requests.append(current_time)
        return RateLimitResult(
            allowed=True,
            remaining=config.max_requests - len(state.requests),
            reset_time=current_time + config.window_seconds,
        )

    @staticmethod
    async def _apply_token_bucket(
        config: RateLimitConfig,
        state: RateLimitState,
        current_time: float,
    ) -> RateLimitResult:
        """Apply token bucket rate limiting."""
        # Refill tokens
        time_passed = current_time - state.last_refill
        refill_amount = time_passed * config.refill_rate
        state.tokens = min(config.burst_capacity, state.tokens + refill_amount)
        state.last_refill = current_time

        if state.tokens >= 1:
            state.tokens -= 1
            return RateLimitResult(
                allowed=True,
                remaining=int(state.tokens),
                reset_time=current_time + (1 / config.refill_rate),
            )
        time_to_next_token = (1 - state.tokens) / config.refill_rate
        return RateLimitResult(
            allowed=False,
            remaining=0,
            reset_time=current_time + time_to_next_token,
            retry_after=int(time_to_next_token),
        )
