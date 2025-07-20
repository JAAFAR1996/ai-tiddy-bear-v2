import json
from datetime import datetime, timedelta

from fastapi import Request, Response

from src.domain.constants import RATE_LIMIT_RETRY_AFTER_SECONDS


class ChildSafeRateLimiter:
    """Rate limiter with child - friendly error messages."""

    def __init__(self) -> None:
        self.request_counts: dict[str, list] = {}
        self.child_endpoints = ["/esp32", "/ai/generate", "/audio", "/voice"]

    def is_rate_limited(self, request: Request) -> bool:
        """Check if request should be rate limited."""
        client_ip = self._get_client_ip(request)
        endpoint = str(request.url.path)

        # Clean old requests (older than 1 minute)
        self._clean_old_requests(client_ip)

        # Check rate limit
        if client_ip not in self.request_counts:
            self.request_counts[client_ip] = []

        current_time = datetime.now()
        self.request_counts[client_ip].append(current_time)

        # Different limits for different endpoints
        if self._is_child_endpoint(endpoint):
            # More restrictive for child endpoints
            return len(self.request_counts[client_ip]) > 20  # 20 requests per minute
        # Standard rate limit
        return len(self.request_counts[client_ip]) > 60  # 60 requests per minute

    def create_rate_limit_response(self, request: Request) -> Response:
        """Create appropriate rate limit response."""
        endpoint = str(request.url.path)
        if self._is_child_endpoint(endpoint):
            return self._create_child_friendly_response()
        return self._create_standard_response()

    def _get_client_ip(self, request: Request) -> str:
        """Extract client IP address."""
        forwarded_for = request.headers.get("X-Forwarded-For")
        if forwarded_for:
            return forwarded_for.split(",")[0].strip()

        real_ip = request.headers.get("X-Real-IP")
        if real_ip:
            return real_ip

        return str(request.client.host if request.client else "unknown")

    def _clean_old_requests(self, client_ip: str) -> None:
        """Remove requests older than 1 minute."""
        if client_ip not in self.request_counts:
            return

        cutoff_time = datetime.now() - timedelta(minutes=1)
        self.request_counts[client_ip] = [
            req_time
            for req_time in self.request_counts[client_ip]
            if req_time > cutoff_time
        ]

        # Clean up empty entries
        if not self.request_counts[client_ip]:
            del self.request_counts[client_ip]

    def _is_child_endpoint(self, endpoint: str) -> bool:
        """Check if endpoint is child - facing."""
        return any(endpoint.startswith(ep) for ep in self.child_endpoints)

    def _create_child_friendly_response(self) -> Response:
        """Create child - friendly rate limit response."""
        message = {
            "message": "Wow, you're really chatty today! Let's take a short break.",
            "child_friendly": True,
            "suggestion": "Maybe we can play a different game?",
            "wait_time": "60 seconds",
        }

        return Response(
            content=json.dumps(message),
            status_code=429,
            media_type="application/json",
            headers={
                "Retry-After": str(RATE_LIMIT_RETRY_AFTER_SECONDS),
                "X-Child-Safety": "active",
                "X-Rate-Limit-Friendly": "true",
            },
        )

    def _create_standard_response(self) -> Response:
        """Create standard rate limit response."""
        message = {
            "detail": "Rate limit exceeded. Please try again later.",
            "retry_after": 60,
        }

        return Response(
            content=json.dumps(message),
            status_code=429,
            media_type="application/json",
            headers={
                "Retry-After": str(RATE_LIMIT_RETRY_AFTER_SECONDS),
                "X-Rate-Limit": "exceeded",
            },
        )
