"""Security Headers Service for AI Teddy Bear application.

Implements comprehensive security headers for protecting against common web vulnerabilities.
Designed for child-safe applications with strict security requirements.
"""

from dataclasses import dataclass
from datetime import datetime, timedelta
from enum import Enum
from typing import Any, Dict

from src.infrastructure.logging_config import get_logger
from src.infrastructure.security.core.security_levels import SecurityLevel

logger = get_logger(__name__, component="security")


class SecurityHeaderType(Enum):
    """Types of security headers."""
    CSP = "content-security-policy"
    HSTS = "strict-transport-security"
    X_FRAME_OPTIONS = "x-frame-options"
    X_CONTENT_TYPE_OPTIONS = "x-content-type-options"
    X_XSS_PROTECTION = "x-xss-protection"
    REFERRER_POLICY = "referrer-policy"
    PERMISSIONS_POLICY = "permissions-policy"


@dataclass
class SecurityHeaderConfig:
    """Configuration for security headers."""
    header_type: SecurityHeaderType
    value: str
    enabled: bool = True
    child_safe: bool = True


class SecurityHeadersService:
    """Service for managing HTTP security headers.

    Provides comprehensive security headers optimized for child-safe applications.
    Implements OWASP security best practices with additional child protection measures.
    """

    def __init__(self, security_level: SecurityLevel = SecurityLevel.CHILD_SAFETY_ENHANCED):
        """Initialize security headers service.

        Args:
            security_level: The security level to apply (CHILD_SAFETY_ENHANCED for production child safety)
        """
        self.security_level = security_level
        self.logger = logger
        self._headers_config = self._build_headers_config()

        self.logger.info(f"SecurityHeadersService initialized with {security_level.value} security level")

    def _build_headers_config(self) -> Dict[SecurityHeaderType, SecurityHeaderConfig]:
        """Build security headers configuration based on security level."""
        config = {}

        # Content Security Policy - Strict for child safety
        csp_value = (
            "default-src 'self'; "
            "script-src 'self' 'unsafe-inline'; "
            "style-src 'self' 'unsafe-inline'; "
            "img-src 'self' data: https:; "
            "font-src 'self'; "
            "connect-src 'self'; "
            "frame-ancestors 'none'; "
            "form-action 'self'"
        )
        config[SecurityHeaderType.CSP] = SecurityHeaderConfig(
            SecurityHeaderType.CSP, csp_value, True, True
        )

        # HSTS - Force HTTPS for child safety
        hsts_value = "max-age=31536000; includeSubDomains; preload"
        config[SecurityHeaderType.HSTS] = SecurityHeaderConfig(
            SecurityHeaderType.HSTS, hsts_value, True, True
        )

        # X-Frame-Options - Prevent clickjacking
        config[SecurityHeaderType.X_FRAME_OPTIONS] = SecurityHeaderConfig(
            SecurityHeaderType.X_FRAME_OPTIONS, "DENY", True, True
        )

        # X-Content-Type-Options - Prevent MIME sniffing
        config[SecurityHeaderType.X_CONTENT_TYPE_OPTIONS] = SecurityHeaderConfig(
            SecurityHeaderType.X_CONTENT_TYPE_OPTIONS, "nosniff", True, True
        )

        # X-XSS-Protection - Enable XSS filtering
        config[SecurityHeaderType.X_XSS_PROTECTION] = SecurityHeaderConfig(
            SecurityHeaderType.X_XSS_PROTECTION, "1; mode=block", True, True
        )

        # Referrer Policy - Strict for privacy
        config[SecurityHeaderType.REFERRER_POLICY] = SecurityHeaderConfig(
            SecurityHeaderType.REFERRER_POLICY, "strict-origin-when-cross-origin", True, True
        )

        # Permissions Policy - Restrict dangerous features
        permissions_value = (
            "geolocation=(), microphone=(), camera=(), "
            "payment=(), usb=(), magnetometer=(), gyroscope=()"
        )
        config[SecurityHeaderType.PERMISSIONS_POLICY] = SecurityHeaderConfig(
            SecurityHeaderType.PERMISSIONS_POLICY, permissions_value, True, True
        )

        return config

    def get_security_headers(self) -> Dict[str, str]:
        """Get all enabled security headers as a dictionary.

        Returns:
            Dict[str, str]: Dictionary of header names and values
        """
        headers = {}

        for header_config in self._headers_config.values():
            if header_config.enabled:
                headers[header_config.header_type.value] = header_config.value

        self.logger.debug(f"Generated {len(headers)} security headers")
        return headers

    def apply_headers_to_response(self, response_headers: Dict[str, str]) -> None:
        """Apply security headers to a response headers dictionary.

        Args:
            response_headers: The response headers dictionary to modify
        """
        security_headers = self.get_security_headers()
        response_headers.update(security_headers)

        self.logger.debug(f"Applied {len(security_headers)} security headers to response")

    def is_header_enabled(self, header_type: SecurityHeaderType) -> bool:
        """Check if a specific security header is enabled.

        Args:
            header_type: The type of header to check

        Returns:
            bool: True if the header is enabled
        """
        config = self._headers_config.get(header_type)
        return config.enabled if config else False

    def get_header_value(self, header_type: SecurityHeaderType) -> str:
        """Get the value for a specific security header.

        Args:
            header_type: The type of header to get

        Returns:
            str: The header value, or empty string if not found/disabled
        """
        config = self._headers_config.get(header_type)
        if config and config.enabled:
            return config.value
        return ""

    def validate_headers(self) -> bool:
        """Validate that all critical security headers are properly configured.

        Returns:
            bool: True if all critical headers are valid
        """
        critical_headers = [
            SecurityHeaderType.CSP,
            SecurityHeaderType.X_FRAME_OPTIONS,
            SecurityHeaderType.X_CONTENT_TYPE_OPTIONS
        ]

        for header_type in critical_headers:
            if not self.is_header_enabled(header_type):
                self.logger.warning(f"Critical security header {header_type.value} is disabled")
                return False

        self.logger.info("All critical security headers are properly configured")
        return True
