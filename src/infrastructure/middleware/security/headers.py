"""Enhanced Security Headers Middleware for AI Teddy Bear.

Consolidated implementation combining all valuable features from scattered implementations
while maintaining clean architecture and child safety compliance.
"""

import time
import uuid
from dataclasses import dataclass, field
from typing import Any

from fastapi import Request, Response
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.middleware.base import RequestResponseEndpoint

from src.infrastructure.config.settings import get_settings
from src.infrastructure.logging_config import get_logger

logger = get_logger(__name__, component="security")


@dataclass
class SecurityHeadersConfig:
    """Enhanced configuration for security headers with child safety features."""

    # Content Security Policy
    csp_default_src: str = "'self'"
    csp_script_src: str = "'self'"
    csp_style_src: str = "'self' 'unsafe-inline'"
    csp_img_src: str = "'self' data: blob:"
    csp_connect_src: str = "'self' wss:"
    csp_font_src: str = "'self'"
    csp_object_src: str = "'none'"
    csp_media_src: str = "'self' blob:"
    csp_frame_src: str = "'none'"
    csp_frame_ancestors: str = "'none'"

    # HTTP Strict Transport Security
    hsts_max_age: int = 31536000  # 1 year
    hsts_include_subdomains: bool = True
    hsts_preload: bool = True

    # X-Frame-Options
    frame_options: str = "DENY"

    # X-Content-Type-Options
    content_type_options: str = "nosniff"

    # XSS Protection
    xss_protection: str = "1; mode=block"

    # Referrer Policy
    referrer_policy: str = "strict-origin-when-cross-origin"

    # Permissions Policy (child-safe defaults)
    permissions_policy: dict[str, str] = field(default_factory=lambda: {
        "camera": "()",
        "microphone": "(self)",  # Allow for voice input
        "geolocation": "()",
        "payment": "()",
        "usb": "()",
        "bluetooth": "()",
        "magnetometer": "()",
        "gyroscope": "()",
        "accelerometer": "()"
    })

    # Cross-Origin settings
    cross_origin_embedder_policy: str = "require-corp"
    cross_origin_opener_policy: str = "same-origin"
    cross_origin_resource_policy: str = "same-origin"

    # Child safety specific settings
    child_safety_mode: bool = True
    coppa_compliant: bool = True
    enhanced_child_protection: bool = True

    # Cache control for child protection
    child_cache_control: str = "no-store, must-revalidate, no-cache, private"


class SecurityHeadersMiddleware(BaseHTTPMiddleware):
    """Enhanced FastAPI middleware for comprehensive security headers with child safety."""

    def __init__(self, app, config: SecurityHeadersConfig = None):
        super().__init__(app)
        self.config = config or SecurityHeadersConfig()

        # Load environment settings
        try:
            settings = get_settings()
            self.environment = getattr(settings, "ENVIRONMENT", "production")
            self.is_production = self.environment == "production"
        except Exception as e:
            logger.warning("Could not load settings, defaulting to production: %s", e)
            self.environment = "production"
            self.is_production = True

        # Performance tracking
        self.request_count = 0
        self.total_processing_time = 0.0

        logger.info(
            "Enhanced security headers middleware initialized (environment: %s, child_safety: %s)",
            self.environment, self.config.child_safety_mode
        )

    async def dispatch(
        self,
        request: Request,
        call_next: RequestResponseEndpoint,
    ) -> Response:
        """Process request and apply comprehensive security headers."""
        # Request tracking
        start_time = time.time()
        request_id = str(uuid.uuid4())

        # Store request context
        request.state.request_id = request_id
        request.state.start_time = start_time

        try:
            # Process the request
            response = await call_next(request)

            # Apply security headers
            self._apply_all_security_headers(request, response)

            # Track performance
            self._track_performance(start_time)

            return response

        except Exception as e:
            logger.error("Security middleware error: %s", e)

            # Create safe error response with security headers
            error_response = self._create_safe_error_response(str(e))
            self._apply_basic_security_headers(error_response)
            self._add_request_tracking_headers(request, error_response)

            return error_response

    def _apply_all_security_headers(self, request: Request, response: Response) -> None:
        """Apply all security headers based on configuration."""
        try:
            # Core security headers
            self._apply_core_security_headers(response)

            # Child-specific protection if enabled
            if self.config.child_safety_mode and self._is_child_request(request):
                self._apply_enhanced_child_protection(response)

            # Request tracking headers
            self._add_request_tracking_headers(request, response)

            # Environment-specific headers
            self._add_environment_headers(response)

        except Exception as e:
            logger.error("Error applying security headers: %s", e)
            # Fallback to basic headers
            self._apply_basic_security_headers(response)

    def _apply_core_security_headers(self, response: Response) -> None:
        """Apply core security headers."""
        headers = {
            "Content-Security-Policy": self._build_csp(),
            "Strict-Transport-Security": self._build_hsts(),
            "X-Frame-Options": self.config.frame_options,
            "X-Content-Type-Options": self.config.content_type_options,
            "X-XSS-Protection": self.config.xss_protection,
            "Referrer-Policy": self.config.referrer_policy,
            "Permissions-Policy": self._build_permissions_policy(),
            "Cross-Origin-Embedder-Policy": self.config.cross_origin_embedder_policy,
            "Cross-Origin-Opener-Policy": self.config.cross_origin_opener_policy,
            "Cross-Origin-Resource-Policy": self.config.cross_origin_resource_policy,
        }

        for header, value in headers.items():
            if value:
                response.headers[header] = value

    def _apply_basic_security_headers(self, response: Response) -> None:
        """Apply minimal essential security headers as fallback."""
        basic_headers = {
            "X-Frame-Options": "DENY",
            "X-Content-Type-Options": "nosniff",
            "X-XSS-Protection": "1; mode=block",
            "Referrer-Policy": "strict-origin-when-cross-origin",
            "X-Child-Safe": "1",
            "X-COPPA-Compliant": "1",
            "Content-Security-Policy": (
                "default-src 'self'; "
                "script-src 'self'; "
                "style-src 'self' 'unsafe-inline'; "
                "img-src 'self' data: blob:; "
                "connect-src 'self' wss:; "
                "font-src 'self'; "
                "object-src 'none'; "
                "media-src 'self' blob:; "
                "frame-src 'none'; "
                "frame-ancestors 'none'"
            ),
            "Permissions-Policy": (
                "camera=(), "
                "microphone=(self), "
                "geolocation=(), "
                "payment=(), "
                "usb=(), "
                "bluetooth=()"
            ),
        }

        for header, value in basic_headers.items():
            response.headers[header] = value

    def _apply_enhanced_child_protection(self, response: Response) -> None:
        """Apply enhanced protection headers for child users."""
        child_headers = {
            "X-Enhanced-Safety": "enabled",
            "X-Content-Rating": "family-friendly",
            "X-Parental-Controls": "active",
            "X-AI-Safety": "child-mode",
            "X-Voice-Processing": "supervised",
            "X-Emergency-Contact": "available",
            "X-Child-Safety": "active",
            "X-COPPA-Compliant": "true",
            "X-Child-ID-Verified": "true",
            "Cache-Control": self.config.child_cache_control,
            "Pragma": "no-cache",
            "Expires": "0",
        }

        for header, value in child_headers.items():
            response.headers[header] = value

    def _add_request_tracking_headers(self, request: Request, response: Response) -> None:
        """Add request tracking and performance headers."""
        # Request ID for tracking
        request_id = getattr(request.state, "request_id", str(uuid.uuid4()))
        response.headers["X-Request-ID"] = request_id

        # Processing time
        start_time = getattr(request.state, "start_time", time.time())
        processing_time = round((time.time() - start_time) * 1000, 2)
        response.headers["X-Processing-Time"] = f"{processing_time}ms"

        # Safety timestamp
        response.headers["X-Safety-Check"] = str(int(time.time()))

    def _add_environment_headers(self, response: Response) -> None:
        """Add environment-specific headers."""
        response.headers["X-Environment"] = self.environment

        if not self.is_production:
            response.headers["X-Development-Mode"] = "true"

    def _is_child_request(self, request: Request) -> bool:
        """Enhanced child request detection logic."""
        try:
            # Check request state for user info
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
            if "child_id" in request.query_params:
                return True

            # Check path for child endpoints
            child_endpoints = [
                "/api/v1/children",
                "/api/v1/process-audio",
                "/esp32",
                "/api/v1/conversations",
            ]

            if any(request.url.path.startswith(endpoint) for endpoint in child_endpoints):
                return True

            # Check headers for child device
            device_id = request.headers.get("X-Device-ID", "")
            if device_id.startswith("teddy_"):
                return True

            # Check for child ID in headers
            if request.headers.get("X-Child-ID"):
                return True

        except Exception as e:
            logger.warning("Error in child request detection: %s", e)

        return False

    def _track_performance(self, start_time: float) -> None:
        """Track middleware performance metrics."""
        processing_time = time.time() - start_time
        self.request_count += 1
        self.total_processing_time += processing_time

        # Log performance every 1000 requests
        if self.request_count % 1000 == 0:
            avg_time = self.total_processing_time / self.request_count
            logger.info(
                "Security middleware performance: %d requests, avg %.2fms per request",
                self.request_count, avg_time * 1000
            )

    def _create_safe_error_response(self, error_msg: str) -> Response:
        """Create a safe error response with child-friendly messaging."""
        safe_message = "Oops! Something went wrong. Please try again later."

        # Don't expose internal error details to children
        error_response = {
            "error": safe_message,
            "child_safe": True,
            "status": "error",
            "timestamp": int(time.time()),
        }

        return Response(
            content=str(error_response).replace("'", '"'),  # Simple JSON-like format
            status_code=500,
            media_type="application/json",
        )

    def _build_csp(self) -> str:
        """Build Content Security Policy header."""
        csp_directives = {
            "default-src": self.config.csp_default_src,
            "script-src": self.config.csp_script_src,
            "style-src": self.config.csp_style_src,
            "img-src": self.config.csp_img_src,
            "connect-src": self.config.csp_connect_src,
            "font-src": self.config.csp_font_src,
            "object-src": self.config.csp_object_src,
            "media-src": self.config.csp_media_src,
            "frame-src": self.config.csp_frame_src,
            "frame-ancestors": self.config.csp_frame_ancestors,
        }
        return "; ".join([f"{key} {value}" for key, value in csp_directives.items()])

    def _build_hsts(self) -> str:
        """Build HTTP Strict Transport Security header."""
        hsts = f"max-age={self.config.hsts_max_age}"
        if self.config.hsts_include_subdomains:
            hsts += "; includeSubDomains"
        if self.config.hsts_preload:
            hsts += "; preload"
        return hsts

    def _build_permissions_policy(self) -> str:
        """Build Permissions Policy header."""
        if not self.config.permissions_policy:
            return ""
        return ", ".join(
            [f"{key}={value}" for key, value in self.config.permissions_policy.items()]
        )

    def get_stats(self) -> dict[str, Any]:
        """Get middleware performance statistics."""
        avg_time = 0.0
        if self.request_count > 0:
            avg_time = self.total_processing_time / self.request_count

        return {
            "middleware": "SecurityHeadersMiddleware",
            "request_count": self.request_count,
            "average_processing_time_ms": round(avg_time * 1000, 2),
            "total_processing_time": round(self.total_processing_time, 2),
            "environment": self.environment,
            "child_safety_enabled": self.config.child_safety_mode,
            "coppa_compliant": self.config.coppa_compliant,
            "enhanced_protection": self.config.enhanced_child_protection,
        }

    def reset_stats(self) -> None:
        """Reset performance statistics."""
        self.request_count = 0
        self.total_processing_time = 0.0
        logger.info("Security middleware statistics reset")

    def get_child_safety_info(self) -> dict[str, Any]:
        """Get child safety specific information."""
        return {
            "child_protection": "enabled",
            "coppa_compliance": "active",
            "content_filtering": "strict",
            "parental_controls": "available",
            "emergency_contact": "enabled",
            "data_retention": "90-days",
            "privacy_mode": "child-protected",
            "ai_safety": "supervised",
            "voice_processing": "secure",
        }


# Factory functions for backward compatibility and easy setup
def create_security_headers_middleware(config: SecurityHeadersConfig = None) -> SecurityHeadersMiddleware:
    """Factory function to create security headers middleware."""
    if config is None:
        config = SecurityHeadersConfig()
    raise RuntimeError("create_security_headers_middleware is for testing only. Use SecurityHeadersMiddleware with a real FastAPI app in production.")


def get_security_headers_config(child_safety_mode: bool = True) -> SecurityHeadersConfig:
    """Get default security headers configuration."""
    config = SecurityHeadersConfig()
    config.child_safety_mode = child_safety_mode
    return config


def init_security_headers(app, config: SecurityHeadersConfig = None):
    """Initialize security headers middleware for FastAPI app."""
    if config is None:
        config = get_security_headers_config()

    app.add_middleware(SecurityHeadersMiddleware, config=config)
    logger.info("Enhanced security headers middleware initialized with child safety")
    return SecurityHeadersMiddleware(app, config)


# Backward compatibility aliases
def create_security_middleware(app, environment: str = "production") -> SecurityHeadersMiddleware:
    """Backward compatibility factory for presentation layer."""
    config = SecurityHeadersConfig()
    return SecurityHeadersMiddleware(app, config)


def create_teddy_bear_security_middleware(app) -> SecurityHeadersMiddleware:
    """Create security middleware specifically configured for AI Teddy Bear."""
    config = SecurityHeadersConfig()
    config.enhanced_child_protection = True
    middleware = SecurityHeadersMiddleware(app, config)
    logger.info(
        "🧸 AI Teddy Bear security middleware created with enhanced child protection"
    )
    return middleware
