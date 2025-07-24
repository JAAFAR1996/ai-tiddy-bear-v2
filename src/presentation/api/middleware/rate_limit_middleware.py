from collections.abc import Callable

from fastapi import Request, Response, status
from starlette.middleware.base import BaseHTTPMiddleware

from src.infrastructure.logging_config import get_logger
from src.infrastructure.security.rate_limiter.core import RateLimitResult
from src.infrastructure.security.rate_limiter.service import get_rate_limiter

logger = get_logger(__name__, component="middleware")


class RateLimitMiddleware(BaseHTTPMiddleware):
    """Rate limiting middleware that applies different limits based on endpoint patterns.
    Features:
    - Endpoint-specific rate limiting
    - IP-based and user-based limits
    - Child safety rate limits
    - Automatic blocking for abuse
    - Comprehensive headers for client information
    """

    def __init__(
        self,
        app,
        default_config: str = "api_general",
        enable_child_safety: bool = True,
    ):
        super().__init__(app)
        self.rate_limiter = get_rate_limiter()
        self.default_config = default_config
        self.enable_child_safety = enable_child_safety

        # Define endpoint-specific rate limiting rules
        self.endpoint_configs = {
            "/api/auth/login": "auth_login",
            "/api/auth/logout": "api_general",
            "/api/auth/register": "auth_login",
            "/api/children": "child_data_access",
            "/api/children/": "child_data_access",
            "/api/conversations": "child_interaction",
            "/api/conversations/": "child_interaction",
            "/api/interact": "child_interaction",
            "/api/voice": "child_interaction",
        }

    async def dispatch(self, request: Request, call_next: Callable) -> Response:
        """Apply rate limiting to incoming requests."""
        # Extract request information
        client_ip = self._get_client_ip(request)
        user_id = self._get_user_id(request)
        child_id = self._get_child_id(request)
        endpoint = str(request.url.path)

        # Determine rate limiting configuration
        config_name = self._get_rate_limit_config(endpoint)
        rate_limit_key = self._generate_rate_limit_key(request, config_name)

        try:
            # Check rate limits
            result = await self.rate_limiter.check_rate_limit(
                key=rate_limit_key,
                config_name=config_name,
                user_id=user_id,
                child_id=child_id,
                ip_address=client_ip,
                request_details={
                    "method": request.method,
                    "endpoint": endpoint,
                    "user_agent": request.headers.get("user-agent", ""),
                    "referer": request.headers.get("referer", ""),
                },
            )

            # Add rate limit headers to response
            def add_rate_limit_headers(response: Response) -> Response:
                response.headers["X-RateLimit-Limit"] = str(
                    self._get_config_limit(config_name)
                )
                response.headers["X-RateLimit-Remaining"] = str(
                    max(0, result.remaining)
                )
                response.headers["X-RateLimit-Reset"] = str(int(result.reset_time))

                if result.retry_after:
                    response.headers["Retry-After"] = str(result.retry_after)

                if result.child_safety_triggered:
                    response.headers["X-Child-Safety"] = "rate-limit-enforced"

                return response

            # Check if request is allowed
            if not result.allowed:
                # Log rate limit violation
                logger.warning(
                    f"Rate limit exceeded for {rate_limit_key} on {endpoint} "
                    f"(config: {config_name}, reason: {result.blocked_reason})"
                )

                # Return rate limit error response
                error_response = self._create_rate_limit_error_response(
                    result, config_name
                )
                return add_rate_limit_headers(error_response)

            # Process the request
            response = await call_next(request)

            # Add rate limiting headers
            return add_rate_limit_headers(response)

        except Exception as e:
            logger.error(f"Rate limiting error for {endpoint}: {e}")

            # On error, allow request but log the issue
            response = await call_next(request)
            response.headers["X-RateLimit-Error"] = "rate-limit-check-failed"
            return response

    def _get_client_ip(self, request: Request) -> str:
        """Extract client IP address from request."""
        # Check for forwarded IP (from load balancer/proxy)
        forwarded_for = request.headers.get("x-forwarded-for")
        if forwarded_for:
            return forwarded_for.split(",")[0].strip()

        # Check for real IP (from some proxies)
        real_ip = request.headers.get("x-real-ip")
        if real_ip:
            return real_ip

        # Fallback to direct client IP
        if hasattr(request, "client") and request.client:
            return request.client.host

        return "unknown"

    def _get_user_id(self, request: Request) -> str | None:
        """Extract user ID from request(from authentication)."""
        try:
            # Check if user is authenticated
            if hasattr(request.state, "user"):
                user = request.state.user
                if hasattr(user, "id"):
                    return str(user.id)
                if hasattr(user, "email"):
                    return user.email

            # Check for user ID in headers (from JWT or session)
            user_id = request.headers.get("x-user-id")
            if user_id:
                return user_id

            return None
        except (AttributeError, KeyError, ValueError) as e:
            logger.warning(f"Error extracting user ID from request: {e}")
            return None
        except Exception as e:
            logger.error(f"Unexpected error extracting user ID: {e}")
            return None

    def _get_child_id(self, request: Request) -> str | None:
        """Extract child ID from request path or body."""
        try:
            # Check path parameters
            path_parts = str(request.url.path).split("/")

            # Look for child ID in common patterns
            if "children" in path_parts:
                children_index = path_parts.index("children")
                if len(path_parts) > children_index + 1:
                    potential_id = path_parts[children_index + 1]
                    # Simple validation - should be UUID-like
                    if len(potential_id) > 10 and (
                        "-" in potential_id or potential_id.isalnum()
                    ):
                        return potential_id

            # Check query parameters
            if hasattr(request, "query_params"):
                child_id = request.query_params.get("child_id")
                if child_id:
                    return child_id

            return None
        except (AttributeError, ValueError, IndexError) as e:
            logger.warning(f"Error extracting child ID from request: {e}")
            return None
        except Exception as e:
            logger.error(f"Unexpected error extracting child ID: {e}")
            return None

    def _get_rate_limit_config(self, endpoint: str) -> str:
        """Determine which rate limiting configuration to use for an endpoint."""
        # Check for exact match
        if endpoint in self.endpoint_configs:
            return self.endpoint_configs[endpoint]

        # Check for prefix matches
        for pattern, config in self.endpoint_configs.items():
            if endpoint.startswith(pattern):
                return config

        # Default configuration
        return self.default_config

    def _generate_rate_limit_key(self, request: Request, config_name: str) -> str:
        """Generate rate limiting key based on request and configuration."""
        client_ip = self._get_client_ip(request)
        user_id = self._get_user_id(request)
        child_id = self._get_child_id(request)

        # For authentication endpoints, use IP address
        if config_name == "auth_login":
            return f"ip:{client_ip}"

        # For child-related endpoints, use child ID if available
        if config_name in ["child_interaction", "child_data_access"] and child_id:
            return f"child:{child_id}"

        # For authenticated users, use user ID
        if user_id:
            return f"user:{user_id}"

        # Fallback to IP address
        return f"ip:{client_ip}"

    def _get_config_limit(self, config_name: str) -> int:
        """Get the request limit for a configuration."""
        config = self.rate_limiter.configs.get(config_name)
        if config:
            return config.max_requests
        return 60  # Default limit

    def _create_rate_limit_error_response(
        self, result: RateLimitResult, config_name: str
    ) -> Response:
        """Create appropriate error response for rate limit violations."""
        # Determine status code based on situation
        if result.child_safety_triggered:
            status_code = status.HTTP_429_TOO_MANY_REQUESTS
            message = (
                "Rate limit exceeded for child safety. Please wait before trying again."
            )
            error_type = "child_safety_rate_limit"
        elif result.blocked_reason:
            status_code = status.HTTP_429_TOO_MANY_REQUESTS
            message = "Too many requests. You have been temporarily blocked."
            error_type = "rate_limit_blocked"
        else:
            status_code = status.HTTP_429_TOO_MANY_REQUESTS
            message = "Rate limit exceeded. Please try again later."
            error_type = "rate_limit_exceeded"

        # Create error response
        error_detail = {
            "error": error_type,
            "message": message,
            "retry_after": result.retry_after,
            "reset_time": result.reset_time,
        }

        # Don't include sensitive timing information for child safety violations
        if result.child_safety_triggered:
            error_detail = {
                "error": "child_safety_rate_limit",
                "message": "Please wait before making another request.",
            }

        response = Response(
            content=f'{{"detail": {error_detail}}}',
            status_code=status_code,
            media_type="application/json",
        )

        return response


def create_rate_limit_middleware(
    app, default_config: str = "api_general", enable_child_safety: bool = True
) -> RateLimitMiddleware:
    """Factory function to create rate limiting middleware."""
    return RateLimitMiddleware(app, default_config, enable_child_safety)


# Middleware configuration for different environments
RATE_LIMIT_CONFIGS = {
    "production": {
        "default_config": "api_general",
        "enable_child_safety": True,
        "strict_mode": True,
    },
    "staging": {
        "default_config": "api_general",
        "enable_child_safety": True,
        "strict_mode": False,
    },
    "development": {
        "default_config": "api_general",
        "enable_child_safety": False,
        "strict_mode": False,
    },
}
