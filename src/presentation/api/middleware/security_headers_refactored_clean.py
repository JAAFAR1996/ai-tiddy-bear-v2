"""from typing import Dict, Any, Optional
import time
import uuid
from fastapi import Request, Response
from fastapi.middleware.base import BaseHTTPMiddleware
from starlette.middleware.base import RequestResponseEndpoint
from .security_headers import SecurityHeadersBuilder, create_headers_builder
from src.infrastructure.config.settings import get_settings.
"""

"""Refactored Security Headers Middleware for AI Teddy Bear
Streamlined implementation using modular components for better maintainability.
"""


class SecurityHeadersMiddleware(BaseHTTPMiddleware):
    """Streamlined security headers middleware for child safety.
    Uses modular components for better maintainability and testing.
    """

    def __init__(self, app) -> None:
        super().__init__(app)
        self.settings = get_settings()
        self.headers_builder = create_headers_builder()
        self.is_production = (
            self.settings.application.ENVIRONMENT == "production"
        )

    async def dispatch(
        self,
        request: Request,
        call_next: RequestResponseEndpoint,
    ) -> Response:
        """Process request and add security headers to response."""
        try:
            # Process the request
            response = await call_next(request)

            # Add security headers
            self._add_security_headers(response, request)

            return response
        except Exception as e:
            # Return safe error response with security headers
            error_response = self._create_safe_error_response(str(e))
            self._add_security_headers(error_response, request)
            return error_response

    def _add_security_headers(
        self, response: Response, request: Request
    ) -> None:
        """Add all required security headers."""
        # Get headers from builder
        headers = self.headers_builder.build_headers(request)

        # Apply headers to response
        for header_name, header_value in headers.items():
            response.headers[header_name] = header_value

        # Add request-specific headers
        self._add_request_specific_headers(response, request)

    def _add_request_specific_headers(
        self,
        response: Response,
        request: Request,
    ) -> None:
        """Add headers specific to the request context."""
        # Add request ID for tracking
        request_id = getattr(request.state, "request_id", str(uuid.uuid4()))
        response.headers["X-Request-ID"] = request_id

        # Add processing time
        start_time = getattr(request.state, "start_time", time.time())
        processing_time = round((time.time() - start_time) * 1000, 2)
        response.headers["X-Processing-Time"] = f"{processing_time}ms"

        # Child safety indicators
        child_id = self._extract_child_id(request)
        if child_id:
            response.headers["X-Child-Safety"] = "active"
            response.headers["X-COPPA-Compliant"] = "true"

    def _extract_child_id(self, request: Request) -> Optional[str]:
        """Extract child ID from request if present."""
        # Check path parameters
        if hasattr(request, "path_params"):
            child_id = request.path_params.get("child_id")
            if child_id:
                return child_id

        # Check headers
        child_id_header = request.headers.get("X-Child-ID")
        if child_id_header:
            return child_id_header

        return None

    def _create_safe_error_response(self, error_msg: str) -> Response:
        """Create a safe error response with child - friendly messaging."""
        safe_message = "Something went wrong. Please try again later."
        return Response(
            content=f'{{"error": "{safe_message}", "child_safe": true}}',
            status_code=500,
            media_type="application/json",
        )


def create_security_middleware(app) -> SecurityHeadersMiddleware:
    """Factory function to create security headers middleware."""
    return SecurityHeadersMiddleware(app)
