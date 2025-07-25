"""Default rate limiting configurations for child safety and security."""

from .core import RateLimitConfig, RateLimitStrategy, RateLimitType


class DefaultConfigurations:
    """Default rate limiting configurations for various scenarios."""

    @staticmethod
    def get_default_configs() -> dict[str, RateLimitConfig]:
        """Get dictionary of default rate limiting configurations."""
        return {
            # Child interaction limits (very strict for safety)
            "child_interaction": RateLimitConfig(
                limit_type=RateLimitType.CHILD_INTERACTION_LIMIT,
                strategy=RateLimitStrategy.SLIDING_WINDOW,
                max_requests=10,  # 10 interactions per minute
                window_seconds=60,
                block_duration_seconds=300,  # 5 minutes
                child_safe_mode=True,
            ),
            # Authentication rate limits
            "auth_login": RateLimitConfig(
                limit_type=RateLimitType.AUTHENTICATION_ATTEMPTS,
                strategy=RateLimitStrategy.FIXED_WINDOW,
                max_requests=5,  # 5 login attempts per 15 minutes
                window_seconds=900,
                block_duration_seconds=3600,  # 1 hour block
                child_safe_mode=True,
            ),
            # Registration rate limits (stricter than login)
            "auth_register": RateLimitConfig(
                limit_type=RateLimitType.AUTHENTICATION_ATTEMPTS,
                strategy=RateLimitStrategy.FIXED_WINDOW,
                max_requests=3,  # 3 registration attempts per hour
                window_seconds=3600,
                block_duration_seconds=7200,  # 2 hour block
                child_safe_mode=True,
            ),
            # Token refresh rate limits
            "auth_refresh": RateLimitConfig(
                limit_type=RateLimitType.AUTHENTICATION_ATTEMPTS,
                strategy=RateLimitStrategy.SLIDING_WINDOW,
                max_requests=10,  # 10 refresh attempts per minute
                window_seconds=60,
                block_duration_seconds=600,  # 10 minute block
                child_safe_mode=True,
            ),
            # API endpoint limits
            "api_general": RateLimitConfig(
                limit_type=RateLimitType.REQUESTS_PER_MINUTE,
                strategy=RateLimitStrategy.TOKEN_BUCKET,
                max_requests=60,  # 60 requests per minute
                window_seconds=60,
                burst_capacity=100,
                refill_rate=1.0,  # 1 token per second
                block_duration_seconds=300,
            ),
            # Child data access limits
            "child_data_access": RateLimitConfig(
                limit_type=RateLimitType.RESOURCE_ACCESS,
                strategy=RateLimitStrategy.SLIDING_WINDOW,
                max_requests=30,  # 30 data access operations per minute
                window_seconds=60,
                block_duration_seconds=600,  # 10 minutes
                child_safe_mode=True,
            ),
        }
