"""from typing import Dict, Any, Optional
import logging
import time
import uuid
from fastapi import Request, Response
from fastapi.middleware.base import BaseHTTPMiddleware
from starlette.middleware.base import RequestResponseEndpoint
from .header_builder import create_headers_builder, SecurityHeadersBuilder
from .header_config import validate_config
from src.infrastructure.config.settings import get_settings.
"""

"""Security Headers Middleware
Main middleware class that coordinates security header application
while maintaining child safety and COPPA compliance.
"""

from src.infrastructure.logging_config import get_logger

logger = get_logger(__name__, component="middleware")


class SecurityHeadersMiddleware(BaseHTTPMiddleware):
    """Provides comprehensive security headers for child safety and COPPA compliance.
    Now modular and maintainable with proper separation of concerns.
    """

    def __init__(self, app, config: Optional[Dict[str, Any]] = None) -> None:
        super().__init__(app)
        self.settings = get_settings()
        self.environment = self.settings.application.ENVIRONMENT

        # Initialize headers builder
        self.headers_builder = create_headers_builder(self.environment)

        # Validate configuration
        validation_results = validate_config(self.headers_builder.config)
        self._log_validation_results(validation_results)

        # Performance monitoring
        self.request_count = 0
        self.total_processing_time = 0.0

        logger.info(
            f"Security headers middleware initialized for {self.environment}"
        )

    async def dispatch(
        self,
        request: Request,
        call_next: RequestResponseEndpoint,
    ) -> Response:
        """Process request and apply security headers
        Args: request: Incoming HTTP request
            call_next: Next middleware / endpoint
        Returns: Response with security headers applied.
        """
        # Track request
        start_time = time.time()
        request_id = str(uuid.uuid4())

        # Store request context
        request.state.request_id = request_id
        request.state.start_time = start_time

        try:
            # Process the request
            response = await call_next(request)

            # Apply security headers
            self._apply_security_headers(request, response)

            # Track performance
            self._track_performance(start_time)

            return response
        except Exception as e:
            logger.error(f"Security middleware error: {e}")

            # Still apply basic security headers even on error
            error_response = Response(
                content="Internal Server Error",
                status_code=500,
                media_type="text/plain",
            )
            self._apply_basic_security_headers(error_response)
            return error_response

    def _apply_security_headers(
        self, request: Request, response: Response
    ) -> None:
        """Apply all security headers to the response."""
        try:
            # Build headers based on request context
            security_headers = self.headers_builder.build_all_headers(request)

            # Apply headers to response
            for name, value in security_headers.items():
                response.headers[name] = value

            # Apply special child safety measures
            if self._is_child_request(request):
                self._apply_enhanced_child_protection(response)
        except Exception as e:
            logger.error(f"Error applying security headers: {e}")

            # Fallback to basic headers
            self._apply_basic_security_headers(response)

    def _apply_basic_security_headers(self, response: Response) -> None:
        """Apply minimal essential security headers as fallback."""
        basic_headers = {
            "X-Frame-Options": "DENY",
            "X-Content-Type-Options": "nosniff",
            "X-XSS-Protection": "1; mode=block",
            "X-Child-Safe": "1",
            "X-COPPA-Compliant": "1",
        }

        for name, value in basic_headers.items():
            response.headers[name] = value

    def _apply_enhanced_child_protection(self, response: Response) -> None:
        """Apply enhanced protection for child users."""
        child_headers = {
            "X-Enhanced-Safety": "enabled",
            "X-Content-Rating": "family-friendly",
            "Cache-Control": "no-store, must-revalidate, no-cache",
            "Pragma": "no-cache",
            "Expires": "0",
        }

        for name, value in child_headers.items():
            response.headers[name] = value

    def _is_child_request(self, request: Request) -> bool:
        """Check if request is from a child user."""
        # Check for child indicators in request
        user = getattr(request.state, "user", None)
        if user and user.get("role") == "child":
            return True

        # Check query parameters for child age
        child_age = request.query_params.get("child_age")
        if child_age:
            try:
                age = int(child_age)
                return age <= 13  # COPPA age limit
            except (ValueError, TypeError):
                pass

        # Check for child_id parameter
        return "child_id" in request.query_params

    def _track_performance(self, start_time: float) -> None:
        """Track middleware performance metrics."""
        processing_time = time.time() - start_time
        self.request_count += 1
        self.total_processing_time += processing_time

        # Log performance every 1000 requests
        if self.request_count % 1000 == 0:
            avg_time = self.total_processing_time / self.request_count
            logger.info(
                f"Security middleware performance: "
                f"{self.request_count} requests, "
                f"avg {avg_time * 1000:.2f}ms per request",
            )

    def _log_validation_results(
        self, validation_results: Dict[str, list]
    ) -> None:
        """Log configuration validation results."""
        for error in validation_results["errors"]:
            logger.error(f"Security config error: {error}")

        for warning in validation_results["warnings"]:
            logger.warning(f"Security config warning: {warning}")

        for recommendation in validation_results["recommendations"]:
            logger.info(f"Security config recommendation: {recommendation}")

    def get_stats(self) -> Dict[str, Any]:
        """Get middleware performance statistics."""
        avg_time = 0.0
        if self.request_count > 0:
            avg_time = self.total_processing_time / self.request_count

        return {
            "request_count": self.request_count,
            "average_processing_time_ms": avg_time * 1000,
            "total_processing_time": self.total_processing_time,
            "environment": self.environment,
            "child_safety_enabled": self.headers_builder.config.child_safety_mode,
        }


# Convenience function for easy setup
def create_security_middleware(
    app,
    environment: str = "production",
) -> SecurityHeadersMiddleware:
    """Create and configure security headers middleware
    Args: app: FastAPI application instance
        environment: Environment configuration
    Returns: Configured SecurityHeadersMiddleware.
    """
    return SecurityHeadersMiddleware(app)
