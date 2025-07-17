"""from dataclasses import dataclass
from enum import Enum
from typing import Dict, List, Optional.
"""

"""Security Headers Configuration
Defines configuration and constants for security headers middleware.
"""


class SecurityLevel(Enum):
    """Security levels for different environments."""

    DEVELOPMENT = "development"
    STAGING = "staging"
    PRODUCTION = "production"


class CSPDirective(Enum):
    """Content Security Policy directive types."""

    DEFAULT_SRC = "default-src"
    SCRIPT_SRC = "script-src"
    STYLE_SRC = "style-src"
    IMG_SRC = "img-src"
    CONNECT_SRC = "connect-src"
    FONT_SRC = "font-src"
    OBJECT_SRC = "object-src"
    MEDIA_SRC = "media-src"
    FRAME_SRC = "frame-src"
    CHILD_SRC = "child-src"
    FORM_ACTION = "form-action"
    FRAME_ANCESTORS = "frame-ancestors"
    BASE_URI = "base-uri"
    MANIFEST_SRC = "manifest-src"
    WORKER_SRC = "worker-src"


@dataclass
class SecurityHeadersConfig:
    """Configuration for security headers."""

    # Basic security headers
    x_content_type_options: str = "nosniff"
    x_frame_options: str = "DENY"
    x_xss_protection: str = "1; mode=block"
    referrer_policy: str = "strict-origin-when-cross-origin"

    # HTTPS and transport security
    strict_transport_security: Optional[str] = None
    expect_ct: Optional[str] = None

    # Content Security Policy
    content_security_policy: Optional[str] = None

    # Permissions Policy (formerly Feature Policy)
    permissions_policy: Optional[str] = None

    # Child safety specific headers
    x_robots_tag: str = "noindex, nofollow, noarchive, nosnippet"
    x_permitted_cross_domain_policies: str = "none"

    # COPPA compliance headers
    x_coppa_compliant: str = "true"
    x_child_safe: str = "true"

    # Custom headers for child protection
    x_parental_controls: str = "enabled"
    x_content_filtering: str = "strict"


class ProductionHeadersConfig(SecurityHeadersConfig):
    """Production - specific security headers configuration."""

    def __init__(self) -> None:
        super().__init__()

        # Strict HTTPS enforcement
        self.strict_transport_security = (
            "max-age=31536000; includeSubDomains; preload"
        )
        self.expect_ct = "max-age=86400, enforce"

        # Strict Content Security Policy for production
        self.content_security_policy = (
            "default-src 'self'; "
            "script-src 'self' 'unsafe-inline' 'unsafe-eval' https://cdn.jsdelivr.net; "
            "style-src 'self' 'unsafe-inline' https://fonts.googleapis.com; "
            "img-src 'self' data: https:; "
            "connect-src 'self' https:; "
            "font-src 'self' https://fonts.gstatic.com; "
            "object-src 'none'; "
            "media-src 'self'; "
            "frame-src 'none'; "
            "form-action 'self'; "
            "frame-ancestors 'none'; "
            "base-uri 'self'; "
            "upgrade-insecure-requests"
        )

        # Strict permissions policy
        self.permissions_policy = (
            "geolocation=(), "
            "microphone=(), "
            "camera=(), "
            "payment=(), "
            "bluetooth=(), "
            "magnetometer=(), "
            "gyroscope=(), "
            "accelerometer=(), "
            "ambient-light-sensor=(), "
            "autoplay=(), "
            "encrypted-media=(), "
            "fullscreen=(), "
            "picture-in-picture=()"
        )


class DevelopmentHeadersConfig(SecurityHeadersConfig):
    """Development - specific security headers configuration."""

    def __init__(self) -> None:
        super().__init__()

        # Relaxed CSP for development
        self.content_security_policy = (
            "default-src 'self' 'unsafe-inline' 'unsafe-eval'; "
            "script-src 'self' 'unsafe-inline' 'unsafe-eval' http://localhost:* https:; "
            "style-src 'self' 'unsafe-inline' https:; "
            "img-src 'self' data: https: http:; "
            "connect-src 'self' http://localhost:* https: ws: wss:; "
            "font-src 'self' https: data:; "
            "object-src 'none'; "
            "media-src 'self' https: http:; "
            "frame-src 'self' http://localhost:*; "
            "form-action 'self'; "
            "base-uri 'self'"
        )

        # Relaxed permissions policy
        self.permissions_policy = (
            "geolocation=(), "
            "microphone=(self), "
            "camera=(self), "
            "payment=(), "
            "bluetooth=(), "
            "autoplay=(self)"
        )


def get_headers_config(security_level: SecurityLevel) -> SecurityHeadersConfig:
    """Get appropriate headers configuration for security level."""
    configs = {
        SecurityLevel.PRODUCTION: ProductionHeadersConfig,
        SecurityLevel.STAGING: ProductionHeadersConfig,  # Use production config for staging
        SecurityLevel.DEVELOPMENT: DevelopmentHeadersConfig,
    }

    config_class = configs.get(security_level, ProductionHeadersConfig)
    return config_class()


# COPPA-specific header constants
COPPA_HEADERS = {
    "X-COPPA-Compliant": "true",
    "X-Child-Safe": "true",
    "X-Parental-Controls": "enabled",
    "X-Content-Filtering": "strict",
    "X-Data-Retention": "90-days",
    "X-Privacy-Policy": "https://aiteddy.com/privacy",
    "X-Terms-Of-Service": "https://aiteddy.com/terms",
}

# Security headers that should always be present
REQUIRED_SECURITY_HEADERS = [
    "X-Content-Type-Options",
    "X-Frame-Options",
    "X-XSS-Protection",
    "Referrer-Policy",
    "Content-Security-Policy",
    "X-COPPA-Compliant",
]

# Headers to remove for security (server information leakage)
HEADERS_TO_REMOVE = [
    "Server",
    "X-Powered-By",
    "X-AspNet-Version",
    "X-AspNetMvc-Version",
]
