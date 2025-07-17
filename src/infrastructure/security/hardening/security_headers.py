"""Security Headers Middleware for AI Teddy Bear.

Comprehensive HTTP security headers for child safety and data protection
"""

from dataclasses import dataclass

from fastapi import Request, Response

from src.infrastructure.logging_config import get_logger

logger = get_logger(__name__, component="security")


@dataclass
class SecurityHeadersConfig:
    """Configuration for security headers."""

    # Content Security Policy
    csp_default_src: str = "'self'"
    csp_script_src: str = "'self' 'unsafe-inline'"
    csp_style_src: str = "'self' 'unsafe-inline'"
    csp_img_src: str = "'self' data: https:"
    csp_connect_src: str = "'self'"
    csp_font_src: str = "'self'"
    csp_object_src: str = "'none'"
    csp_media_src: str = "'self'"
    csp_frame_src: str = "'none'"

    # HTTP Strict Transport Security
    hsts_max_age: int = 31536000  # 1 year
    hsts_include_subdomains: bool = True
    hsts_preload: bool = True

    # X-Frame-Options
    frame_options: str = "DENY"  # or "SAMEORIGIN"

    # X-Content-Type-Options
    content_type_options: str = "nosniff"

    # Referrer Policy
    referrer_policy: str = "strict-origin-when-cross-origin"

    # Permissions Policy (formerly Feature Policy)
    permissions_policy: dict[str, str] = None

    # Cross-Origin settings
    cross_origin_embedder_policy: str = "require-corp"
    cross_origin_opener_policy: str = "same-origin"
    cross_origin_resource_policy: str = "same-origin"

    # Child safety specific headers
    child_safety_mode: bool = True

    def __post_init__(self):
        if self.permissions_policy is None:
            # Child-safe default permissions
            self.permissions_policy = {
                "camera": "none",
                "microphone": "self",  # Allow for voice input
                "geolocation": "none",
                "payment": "none",
                "usb": "none",
                "magnetometer": "none",
                "gyroscope": "none",
                "accelerometer": "none",
            }


class SecurityHeadersMiddleware:
    """FastAPI middleware for adding security headers."""

    def __init__(self, config: SecurityHeadersConfig):
        self.config = config

    async def __call__(self, request: Request, call_next):
        response = await call_next(request)
        self._apply_headers(response)
        return response

    def _apply_headers(self, response: Response) -> None:
        """Apply all configured security headers."""
        headers = {
            "Content-Security-Policy": self._get_csp(),
            "Strict-Transport-Security": self._get_hsts(),
            "X-Frame-Options": self.config.frame_options,
            "X-Content-Type-Options": self.config.content_type_options,
            "Referrer-Policy": self.config.referrer_policy,
            "Permissions-Policy": self._get_permissions_policy(),
            "Cross-Origin-Embedder-Policy": self.config.cross_origin_embedder_policy,
            "Cross-Origin-Opener-Policy": self.config.cross_origin_opener_policy,
            "Cross-Origin-Resource-Policy": self.config.cross_origin_resource_policy,
        }
        for header, value in headers.items():
            if value:
                response.headers[header] = value

    def _get_csp(self) -> str:
        """Construct the Content-Security-Policy header."""
        csp = {
            "default-src": self.config.csp_default_src,
            "script-src": self.config.csp_script_src,
            "style-src": self.config.csp_style_src,
            "img-src": self.config.csp_img_src,
            "connect-src": self.config.csp_connect_src,
            "font-src": self.config.csp_font_src,
            "object-src": self.config.csp_object_src,
            "media-src": self.config.csp_media_src,
            "frame-src": self.config.csp_frame_src,
        }
        return "; ".join([f"{key} {value}" for key, value in csp.items()])

    def _get_hsts(self) -> str:
        """Construct the Strict-Transport-Security header."""
        hsts = f"max-age={self.config.hsts_max_age}"
        if self.config.hsts_include_subdomains:
            hsts += "; includeSubDomains"
        if self.config.hsts_preload:
            hsts += "; preload"
        return hsts

    def _get_permissions_policy(self) -> str:
        """Construct the Permissions-Policy header."""
        if not self.config.permissions_policy:
            return ""
        return ", ".join(
            [
                f"{key}={value}"
                for key, value in self.config.permissions_policy.items()
            ],
        )
