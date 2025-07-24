from .error_handling import ErrorHandlingMiddleware
from .rate_limit_middleware import RateLimitMiddleware as ChildSafetyMiddleware
from .request_logging import RequestLoggingMiddleware

# Re-enabled for production - rate limiting now properly imports from service.py
# RateLimitingMiddleware same as RateLimitMiddleware

__all__ = [
    "ChildSafetyMiddleware",  # Re-enabled for production
    "ErrorHandlingMiddleware",
    "RateLimitMiddleware",  # Re-enabled for production (alias)
    "RequestLoggingMiddleware",
]

# Export alias for backward compatibility
RateLimitMiddleware = ChildSafetyMiddleware
