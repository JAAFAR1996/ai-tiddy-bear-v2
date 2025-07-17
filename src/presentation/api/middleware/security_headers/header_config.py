"""from dataclasses import dataclass, field
from typing import Dict, Any, Optional.
"""

"""Security Headers Configuration
This module provides configuration classes and defaults for security headers
to maintain COPPA compliance and child safety.
"""


@dataclass
class CSPConfig:
    """Content Security Policy configuration."""

    default_src: str = "'self'"
    script_src: str = "'self' 'unsafe-inline'"
    style_src: str = "'self' 'unsafe-inline'"
    img_src: str = "'self' data: https:"
    connect_src: str = "'self'"
    font_src: str = "'self'"
    object_src: str = "'none'"
    media_src: str = "'self'"
    frame_src: str = "'none'"
    child_src: str = "'self'"
    worker_src: str = "'self'"
    manifest_src: str = "'self'"
    base_uri: str = "'self'"
    form_action: str = "'self'"
    frame_ancestors: str = "'none'"
    upgrade_insecure_requests: bool = True


@dataclass
class SecurityHeadersConfig:
    """Comprehensive security headers configuration."""

    # Basic security headers
    x_frame_options: str = "DENY"
    x_content_type_options: str = "nosniff"
    x_xss_protection: str = "1; mode=block"
    referrer_policy: str = "strict-origin-when-cross-origin"

    # HSTS configuration
    hsts_max_age: int = 31536000  # 1 year
    hsts_include_subdomains: bool = True
    hsts_preload: bool = True

    # Content Security Policy
    csp: CSPConfig = field(default_factory=CSPConfig)

    # Permissions Policy (Feature Policy)
    permissions_policy: Dict[str, str] = field(
        default_factory=lambda: {
            "camera": "none",
            "microphone": "self",  # Allow for voice input
            "geolocation": "none",
            "payment": "none",
            "usb": "none",
            "accelerometer": "none",
            "gyroscope": "none",
            "magnetometer": "none",
            "display-capture": "none",
            "fullscreen": "none",
        },
    )

    # Cross-Origin policies
    cross_origin_embedder_policy: str = "require-corp"
    cross_origin_opener_policy: str = "same-origin"
    cross_origin_resource_policy: str = "same-origin"

    # Child safety specific
    child_safety_mode: bool = True
    coppa_compliant: bool = True

    # Custom headers for child safety
    custom_child_headers: Dict[str, str] = field(
        default_factory=lambda: {
            "X-Child-Safe": "1",
            "X-COPPA-Compliant": "1",
            "X-Content-Rating": "family-friendly",
            "X-Privacy-Mode": "child-protected",
        },
    )


def get_production_config() -> SecurityHeadersConfig:
    """Get production - ready security configuration."""
    config = SecurityHeadersConfig()

    # Stricter CSP for production
    config.csp.script_src = "'self'"  # Remove unsafe-inline
    config.csp.style_src = "'self'"  # Remove unsafe-inline
    config.csp.upgrade_insecure_requests = True

    # Enhanced child safety
    config.child_safety_mode = True
    config.coppa_compliant = True

    return config


def get_development_config() -> SecurityHeadersConfig:
    """Get development - friendly configuration."""
    config = SecurityHeadersConfig()

    # More permissive for development
    config.csp.script_src = "'self' 'unsafe-inline' 'unsafe-eval'"
    config.csp.style_src = "'self' 'unsafe-inline'"
    config.hsts_max_age = 0  # Disable HSTS in development

    return config


def validate_config(config: SecurityHeadersConfig) -> Dict[str, list]:
    """Validate security configuration for compliance
    Args: config: Security headers configuration
    Returns: Dict with validation results(errors, warnings, recommendations).
    """
    issues = {"errors": [], "warnings": [], "recommendations": []}

    # Check CSP for child safety
    if "'unsafe-eval'" in config.csp.script_src:
        issues["errors"].append("CSP allows unsafe-eval - dangerous for child safety")
    if "'unsafe-inline'" in config.csp.script_src:
        issues["warnings"].append(
            "CSP allows unsafe-inline scripts - consider using nonces",
        )

    # Check HSTS configuration
    if config.hsts_max_age < 31536000:  # 1 year
        issues["warnings"].append("HSTS max-age less than 1 year")

    # Check child safety mode
    if not config.child_safety_mode:
        issues["recommendations"].append(
            "Enable child safety mode for COPPA compliance",
        )

    # Check frame options
    if config.x_frame_options not in ["DENY", "SAMEORIGIN"]:
        issues["warnings"].append("Frame options should be DENY or SAMEORIGIN")

    return issues
