from typing import Dict, Any
import time
import uuid
from fastapi import Request, Response
from fastapi.middleware.base import BaseHTTPMiddleware
from starlette.middleware.base import RequestResponseEndpoint
from .headers_config import (
    SecurityLevel,
    get_headers_config,
    COPPA_HEADERS,
    REQUIRED_SECURITY_HEADERS,
    HEADERS_TO_REMOVE,
)
from src.infrastructure.logging_config import get_logger

logger = get_logger(__name__, component="middleware")


class SecurityHeadersMiddleware(BaseHTTPMiddleware):
    """
    Streamlined security headers middleware for child safety.
    Features:
     - COPPA compliance headers
     - Essential security headers
     - Child safety indicators
     - Performance monitoring
    """

    def __init__(
        self, app, security_level: SecurityLevel = SecurityLevel.PRODUCTION
    ) -> None:
        """Initialize middleware with security configuration."""
        super().__init__(app)
        self.security_level = security_level
        self.config = get_headers_config(security_level)
        self.is_production = security_level == SecurityLevel.PRODUCTION
        logger.info(
            f"Security headers middleware initialized for {security_level.value}"
        )

    async def dispatch(
        self, request: Request, call_next: RequestResponseEndpoint
    ) -> Response:
        """
        Process request and add security headers.
        Args:
            request: Incoming HTTP request
            call_next: Next middleware / endpoint
        Returns:
            Response with security headers
        """
        # Generate request tracking ID
        request_id = str(uuid.uuid4())
        request.state.request_id = request_id

        # Record start time for performance monitoring
        start_time = time.time()

        try:
            # Process the request
            response = await call_next(request)

            # Add security headers to response
            self._add_security_headers(response, request)

            # Add performance headers
            self._add_performance_headers(response, start_time)

            # Remove information disclosure headers
            self._remove_disclosure_headers(response)

            return response
        except Exception as e:
            logger.error(f"Error in security headers middleware: {e}")

            # Create minimal error response with security headers
            response = Response(
                content="Internal Server Error",
                status_code=500,
                headers={"Content-Type": "text/plain"},
            )
            self._add_essential_headers(response, request)
            return response

    def _add_security_headers(
        self, response: Response, request: Request
    ) -> None:
        """Add comprehensive security headers to response."""
        # Core security headers
        response.headers["X-Content-Type-Options"] = (
            self.config.x_content_type_options
        )
        response.headers["X-Frame-Options"] = self.config.x_frame_options
        response.headers["X-XSS-Protection"] = self.config.x_xss_protection
        response.headers["Referrer-Policy"] = self.config.referrer_policy

        # HTTPS security (production only)
        if self.is_production and self.config.strict_transport_security:
            response.headers["Strict-Transport-Security"] = (
                self.config.strict_transport_security
            )

        if self.config.expect_ct:
            response.headers["Expect-CT"] = self.config.expect_ct

        # Content Security Policy
        if self.config.content_security_policy:
            response.headers["Content-Security-Policy"] = (
                self.config.content_security_policy
            )

        # Permissions Policy
        if self.config.permissions_policy:
            response.headers["Permissions-Policy"] = (
                self.config.permissions_policy
            )

        # Additional security headers
        response.headers["X-Robots-Tag"] = self.config.x_robots_tag
        response.headers["X-Permitted-Cross-Domain-Policies"] = (
            self.config.x_permitted_cross_domain_policies
        )

        # COPPA compliance headers
        for header_name, header_value in COPPA_HEADERS.items():
            response.headers[header_name] = header_value

        # Request tracking
        response.headers["X-Request-ID"] = request.state.request_id

    def _add_essential_headers(
        self, response: Response, request: Request
    ) -> None:
        """Add only essential security headers(for error responses)."""
        response.headers["X-Content-Type-Options"] = "nosniff"
        response.headers["X-Frame-Options"] = "DENY"
        response.headers["X-COPPA-Compliant"] = "true"
        response.headers["X-Request-ID"] = getattr(
            request.state, "request_id", str(uuid.uuid4())
        )

    def _add_performance_headers(
        self, response: Response, start_time: float
    ) -> None:
        """Add performance monitoring headers."""
        processing_time = time.time() - start_time

        # Add processing time (useful for monitoring)
        response.headers["X-Processing-Time"] = f"{processing_time:.3f}s"

        # Add timestamp
        response.headers["X-Timestamp"] = str(int(time.time()))

        # Add cache control for child data
        if self._is_child_data_endpoint(response):
            response.headers["Cache-Control"] = (
                "no-store, no-cache, must-revalidate, private"
            )
            response.headers["Pragma"] = "no-cache"
            response.headers["Expires"] = "0"

    def _remove_disclosure_headers(self, response: Response) -> None:
        """Remove headers that could disclose server information."""
        for header_name in HEADERS_TO_REMOVE:
            if header_name in response.headers:
                del response.headers[header_name]

    def _is_child_data_endpoint(self, response: Response) -> bool:
        """Check if this response contains child data."""
        # Simple heuristic - look for child-related content type or headers
        content_type = response.headers.get("Content-Type", "")
        return (
            "child" in content_type.lower()
            or "X-Child-Data" in response.headers
        )

    def validate_headers(self, response: Response) -> Dict[str, bool]:
        """
        Validate that required security headers are present.
        Returns:
            Dict mapping header names to presence status
        """
        validation_results = {}
        for header_name in REQUIRED_SECURITY_HEADERS:
            validation_results[header_name] = header_name in response.headers
        return validation_results

    def get_security_report(self, response: Response) -> Dict[str, Any]:
        """
        Generate security report for this response.
        Returns:
            Security analysis report
        """
        validation_results = self.validate_headers(response)
        return {
            "security_level": self.security_level.value,
            "headers_validation": validation_results,
            "all_required_present": all(validation_results.values()),
            "coppa_compliant": "X-COPPA-Compliant" in response.headers,
            "child_safe": "X-Child-Safe" in response.headers,
            "total_headers": len(response.headers),
            "timestamp": time.time(),
        }


def create_security_headers_middleware(
    security_level: str = "production",
) -> SecurityHeadersMiddleware:
    """
    Factory function to create security headers middleware.
    Args:
        security_level: Security level(development, staging, production)
    Returns:
        Configured SecurityHeadersMiddleware instance
    """
    try:
        level = SecurityLevel(security_level.lower())
    except ValueError:
        logger.warning(
            f"Invalid security level '{security_level}', defaulting to production"
        )
        level = SecurityLevel.PRODUCTION

    return SecurityHeadersMiddleware(app=None, security_level=level)
