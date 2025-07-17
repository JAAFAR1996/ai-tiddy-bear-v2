from dataclasses import dataclass
from datetime import datetime, timedelta
from enum import Enum
from typing import Dict, List, Optional, Set, Any

from src.infrastructure.logging_config import get_logger

logger = get_logger(__name__, component="security")


class SecurityLevel(Enum):
    """Security levels for different application contexts."""

    CHILD_STRICT = "child_strict"  # Maximum protection for child interactions
    PARENT_MODERATE = (
        "parent_moderate"  # Balanced security for parent interfaces
    )
    ADMIN_STRICT = "admin_strict"  # High security for admin interfaces
    DEVELOPMENT = "development"  # Relaxed for development


@dataclass
class SecurityHeadersConfiguration:
    """Configuration for security headers with child safety focus."""

    # Content Security Policy
    csp_default_src: Set[str]
    csp_script_src: Set[str]
    csp_style_src: Set[str]
    csp_img_src: Set[str]
    csp_connect_src: Set[str]
    csp_font_src: Set[str]
    csp_frame_src: Set[str]
    csp_media_src: Set[str]

    # Transport Security
    hsts_max_age: int
    hsts_include_subdomains: bool
    hsts_preload: bool

    # Content Protection
    x_content_type_options: str
    x_frame_options: str
    x_xss_protection: str
    referrer_policy: str

    # Child Safety Specific
    child_safety_enabled: bool
    coppa_compliant: bool
    parental_controls_required: bool

    # Cache and Performance
    cache_control: str
    pragma: str
    expires: Optional[str]

    # Custom Headers
    custom_headers: Dict[str, str]


class SecurityHeadersService:
    """
    Enterprise security headers service with child safety focus.
    Features:
    - COPPA - compliant security headers
    - Child - safe Content Security Policy
    - Anti - clickjacking protection
    - XSS prevention
    - Transport security enforcement
    - Custom child safety headers
    """

    def __init__(
        self, default_level: SecurityLevel = SecurityLevel.CHILD_STRICT
    ) -> None:
        """Initialize security headers service."""
        self.default_level = default_level
        self.configurations = self._initialize_configurations()
        self.nonce_cache: Dict[str, datetime] = {}
        self.max_nonce_age = timedelta(hours=1)
        logger.info(
            f"Security headers service initialized with {default_level.value} level"
        )

    def _initialize_configurations(
        self,
    ) -> Dict[SecurityLevel, SecurityHeadersConfiguration]:
        """Initialize security configurations for different levels."""
        return {
            SecurityLevel.CHILD_STRICT: SecurityHeadersConfiguration(
                # Extremely restrictive CSP for child safety
                csp_default_src={"'self'"},
                csp_script_src={"'self'", "'nonce-{nonce}'"},
                csp_style_src={
                    "'self'",
                    "'unsafe-inline'",
                },  # Needed for some child-friendly styling
                csp_img_src={"'self'", "data:", "https://cdn.ai-teddy.com"},
                csp_connect_src={"'self'", "https://api.ai-teddy.com"},
                csp_font_src={"'self'", "https://fonts.googleapis.com"},
                csp_frame_src={"'none'"},  # No framing for children
                csp_media_src={"'self'", "https://media.ai-teddy.com"},
                # Strict transport security
                hsts_max_age=31536000,  # 1 year
                hsts_include_subdomains=True,
                hsts_preload=True,
                # Content protection
                x_content_type_options="nosniff",
                x_frame_options="DENY",
                x_xss_protection="1; mode=block",
                referrer_policy="strict-origin-when-cross-origin",
                # Child safety
                child_safety_enabled=True,
                coppa_compliant=True,
                parental_controls_required=True,
                # Cache control
                cache_control="no-cache, no-store, must-revalidate",
                pragma="no-cache",
                expires="0",
                # Custom child safety headers
                custom_headers={
                    "X-Child-Safety-Mode": "strict",
                    "X-COPPA-Compliant": "true",
                    "X-Parental-Controls": "required",
                    "X-Content-Safety-Level": "child-safe",
                    "X-Age-Verification": "required",
                },
            ),
            SecurityLevel.PARENT_MODERATE: SecurityHeadersConfiguration(
                # Balanced CSP for parent interfaces
                csp_default_src={"'self'"},
                csp_script_src={
                    "'self'",
                    "'unsafe-inline'",
                    "https://cdn.ai-teddy.com",
                },
                csp_style_src={
                    "'self'",
                    "'unsafe-inline'",
                    "https://cdn.ai-teddy.com",
                },
                csp_img_src={"'self'", "data:", "https:", "blob:"},
                csp_connect_src={"'self'", "https:", "wss:"},
                csp_font_src={"'self'", "https:", "data:"},
                csp_frame_src={"'self'", "https://secure.ai-teddy.com"},
                csp_media_src={"'self'", "https:", "blob:"},
                # Standard HSTS
                hsts_max_age=31536000,
                hsts_include_subdomains=True,
                hsts_preload=False,
                # Content protection
                x_content_type_options="nosniff",
                x_frame_options="SAMEORIGIN",
                x_xss_protection="1; mode=block",
                referrer_policy="strict-origin-when-cross-origin",
                # Child safety
                child_safety_enabled=True,
                coppa_compliant=True,
                parental_controls_required=False,
                # Cache control
                cache_control="private, max-age=3600",
                pragma="",
                expires=None,
                # Custom headers
                custom_headers={
                    "X-Parent-Interface": "true",
                    "X-Child-Data-Access": "authorized",
                    "X-COPPA-Compliant": "true",
                },
            ),
            SecurityLevel.ADMIN_STRICT: SecurityHeadersConfiguration(
                # Strict CSP for admin interfaces
                csp_default_src={"'self'"},
                csp_script_src={"'self'", "'nonce-{nonce}'"},
                csp_style_src={"'self'", "'nonce-{nonce}'"},
                csp_img_src={"'self'", "data:"},
                csp_connect_src={"'self'"},
                csp_font_src={"'self'"},
                csp_frame_src={"'none'"},
                csp_media_src={"'none'"},
                # Maximum HSTS
                hsts_max_age=63072000,  # 2 years
                hsts_include_subdomains=True,
                hsts_preload=True,
                # Maximum content protection
                x_content_type_options="nosniff",
                x_frame_options="DENY",
                x_xss_protection="1; mode=block",
                referrer_policy="no-referrer",
                # Child safety
                child_safety_enabled=False,
                coppa_compliant=True,
                parental_controls_required=False,
                # Cache control
                cache_control="no-cache, no-store, must-revalidate",
                pragma="no-cache",
                expires="0",
                # Custom headers
                custom_headers={
                    "X-Admin-Interface": "true",
                    "X-Privileged-Access": "true",
                    "X-Security-Level": "maximum",
                },
            ),
            SecurityLevel.DEVELOPMENT: SecurityHeadersConfiguration(
                # Relaxed CSP for development
                csp_default_src={"'self'", "'unsafe-inline'", "'unsafe-eval'"},
                csp_script_src={
                    "'self'",
                    "'unsafe-inline'",
                    "'unsafe-eval'",
                    "http:",
                    "https:",
                },
                csp_style_src={"'self'", "'unsafe-inline'", "http:", "https:"},
                csp_img_src={"'self'", "data:", "http:", "https:", "blob:"},
                csp_connect_src={"'self'", "http:", "https:", "ws:", "wss:"},
                csp_font_src={"'self'", "http:", "https:", "data:"},
                csp_frame_src={"'self'", "http:", "https:"},
                csp_media_src={"'self'", "http:", "https:", "blob:"},
                # Minimal HSTS for development
                hsts_max_age=0,
                hsts_include_subdomains=False,
                hsts_preload=False,
                # Relaxed content protection
                x_content_type_options="nosniff",
                x_frame_options="SAMEORIGIN",
                x_xss_protection="0",  # Disabled for development debugging
                referrer_policy="unsafe-url",
                # Child safety
                child_safety_enabled=False,
                coppa_compliant=False,
                parental_controls_required=False,
                # Cache control
                cache_control="no-cache",
                pragma="",
                expires=None,
                # Custom headers
                custom_headers={
                    "X-Development-Mode": "true",
                    "X-Debug-Enabled": "true",
                },
            ),
        }

    def get_security_headers(
        self,
        level: Optional[SecurityLevel] = None,
        nonce: Optional[str] = None,
        custom_headers: Optional[Dict[str, str]] = None,
    ) -> Dict[str, str]:
        """
        Generate comprehensive security headers.
        Args:
            level: Security level to apply
            nonce: CSP nonce for inline scripts / styles
            custom_headers: Additional custom headers
        Returns:
            Dict of HTTP security headers
        """
        level = level or self.default_level
        config = self.configurations[level]

        # Generate nonce if needed
        if nonce is None and "{nonce}" in str(config.csp_script_src):
            nonce = self._generate_nonce()

        headers = {}

        # Content Security Policy
        csp = self._build_csp_header(config, nonce)
        if csp:
            headers["Content-Security-Policy"] = csp

        # HTTP Strict Transport Security
        if config.hsts_max_age > 0:
            hsts_value = f"max-age={config.hsts_max_age}"
            if config.hsts_include_subdomains:
                hsts_value += "; includeSubDomains"
            if config.hsts_preload:
                hsts_value += "; preload"
            headers["Strict-Transport-Security"] = hsts_value

        # Content protection headers
        headers.update(
            {
                "X-Content-Type-Options": config.x_content_type_options,
                "X-Frame-Options": config.x_frame_options,
                "X-XSS-Protection": config.x_xss_protection,
                "Referrer-Policy": config.referrer_policy,
            }
        )

        # Cache control
        if config.cache_control:
            headers["Cache-Control"] = config.cache_control
        if config.pragma:
            headers["Pragma"] = config.pragma
        if config.expires:
            headers["Expires"] = config.expires

        # Child safety and COPPA headers
        if config.child_safety_enabled:
            headers["X-Child-Safety-Enabled"] = "true"
        if config.coppa_compliant:
            headers["X-COPPA-Compliant"] = "true"
        if config.parental_controls_required:
            headers["X-Parental-Controls-Required"] = "true"

        # Additional security headers
        headers.update(
            {
                "X-Permitted-Cross-Domain-Policies": "none",
                "X-Download-Options": "noopen",
                "X-DNS-Prefetch-Control": "off",
                "X-Robots-Tag": "noindex, nofollow, nosnippet, noarchive",
                "X-Content-Safety-Scan": "enabled",
            }
        )

        # Custom headers from configuration
        headers.update(config.custom_headers)

        # Additional custom headers from parameter
        if custom_headers:
            headers.update(custom_headers)

        # Add security metadata
        headers.update(
            {
                "X-Security-Level": level.value,
                "X-Security-Headers-Version": "1.0",
                "X-Generated-At": datetime.utcnow().isoformat() + "Z",
            }
        )

        logger.debug(
            f"Generated {len(headers)} security headers for level {level.value}"
        )
        return headers

    def get_child_safety_headers(
        self, child_age: Optional[int] = None, parental_consent: bool = False
    ) -> Dict[str, str]:
        """
        Get specialized headers for child safety.
        Args:
            child_age: Child's age for age-appropriate headers
            parental_consent: Whether parental consent is verified
        Returns:
            Dict of child safety headers
        """
        headers = {
            "X-Child-Safety-Mode": "enabled",
            "X-Content-Filter": "strict",
            "X-Age-Appropriate": "verified",
            "X-Parental-Consent": (
                "verified" if parental_consent else "required"
            ),
        }

        if child_age is not None:
            headers.update(
                {
                    "X-Child-Age-Group": self._get_age_group(child_age),
                    "X-Content-Rating": self._get_content_rating(child_age),
                    "X-COPPA-Subject": "true" if child_age < 13 else "false",
                }
            )

        return headers

    def validate_security_headers(
        self, headers: Dict[str, str]
    ) -> Dict[str, Any]:
        """
        Validate that response has appropriate security headers.
        Args:
            headers: HTTP response headers to validate
        Returns:
            Validation result with recommendations
        """
        required_headers = {
            "Content-Security-Policy",
            "X-Content-Type-Options",
            "X-Frame-Options",
            "X-XSS-Protection",
            "Referrer-Policy",
        }

        missing_headers = required_headers - set(headers.keys())
        weak_configurations = []
        recommendations = []

        # Check for missing critical headers
        if missing_headers:
            recommendations.append(
                f"Add missing security headers: {', '.join(missing_headers)}"
            )

        # Validate CSP
        if "Content-Security-Policy" in headers:
            csp_issues = self._validate_csp(headers["Content-Security-Policy"])
            weak_configurations.extend(csp_issues)

        # Check X-Frame-Options
        if headers.get("X-Frame-Options") not in ["DENY", "SAMEORIGIN"]:
            weak_configurations.append(
                "X-Frame-Options should be DENY or SAMEORIGIN"
            )

        # Check HSTS for HTTPS
        if "Strict-Transport-Security" not in headers:
            recommendations.append("Add HSTS header for HTTPS security")

        # Child safety validation
        if "X-Child-Safety-Enabled" not in headers:
            recommendations.append("Consider adding child safety headers")

        return {
            "secure": len(missing_headers) == 0
            and len(weak_configurations) == 0,
            "missing_headers": list(missing_headers),
            "weak_configurations": weak_configurations,
            "recommendations": recommendations,
            "security_score": self._calculate_security_score(headers),
        }

    def _build_csp_header(
        self, config: SecurityHeadersConfiguration, nonce: Optional[str] = None
    ) -> str:
        """Build Content Security Policy header."""
        directives = []

        # Replace nonce placeholder
        def format_sources(sources: Set[str]) -> str:
            formatted = []
            for source in sources:
                if nonce and "{nonce}" in source:
                    formatted.append(source.format(nonce=nonce))
                else:
                    formatted.append(source)
            return " ".join(sorted(formatted))

        # Build CSP directives
        if config.csp_default_src:
            directives.append(
                f"default-src {format_sources(config.csp_default_src)}"
            )
        if config.csp_script_src:
            directives.append(
                f"script-src {format_sources(config.csp_script_src)}"
            )
        if config.csp_style_src:
            directives.append(
                f"style-src {format_sources(config.csp_style_src)}"
            )
        if config.csp_img_src:
            directives.append(f"img-src {format_sources(config.csp_img_src)}")
        if config.csp_connect_src:
            directives.append(
                f"connect-src {format_sources(config.csp_connect_src)}"
            )
        if config.csp_font_src:
            directives.append(
                f"font-src {format_sources(config.csp_font_src)}"
            )
        if config.csp_frame_src:
            directives.append(
                f"frame-src {format_sources(config.csp_frame_src)}"
            )
        if config.csp_media_src:
            directives.append(
                f"media-src {format_sources(config.csp_media_src)}"
            )

        # Add additional security directives
        directives.extend(
            [
                "object-src 'none'",
                "base-uri 'self'",
                "frame-ancestors 'none'",
                "form-action 'self'",
                "upgrade-insecure-requests",
            ]
        )

        return "; ".join(directives)

    def _generate_nonce(self) -> str:
        """Generate cryptographically secure nonce for CSP."""
        import secrets
        import base64

        # Generate 128-bit random nonce
        nonce_bytes = secrets.token_bytes(16)
        nonce = base64.b64encode(nonce_bytes).decode("ascii")

        # Store in cache with expiration
        self.nonce_cache[nonce] = datetime.utcnow()

        # Clean old nonces
        self._cleanup_nonce_cache()

        return nonce

    def _cleanup_nonce_cache(self) -> None:
        """Remove expired nonces from cache."""
        cutoff = datetime.utcnow() - self.max_nonce_age
        expired_nonces = [
            nonce
            for nonce, created in self.nonce_cache.items()
            if created < cutoff
        ]
        for nonce in expired_nonces:
            del self.nonce_cache[nonce]

    def _get_age_group(self, age: int) -> str:
        """Get age group classification."""
        if age <= 4:
            return "toddler"
        elif age <= 7:
            return "preschool"
        elif age <= 12:
            return "school-age"
        else:
            return "teen"

    def _get_content_rating(self, age: int) -> str:
        """Get appropriate content rating for age."""
        if age <= 4:
            return "G"  # General audiences
        elif age <= 7:
            return "G"
        elif age <= 12:
            return "PG"  # Parental guidance
        else:
            return "PG-13"

    def _validate_csp(self, csp_header: str) -> List[str]:
        """Validate Content Security Policy for common issues."""
        issues = []

        # Check for unsafe configurations
        if "'unsafe - eval'" in csp_header:
            issues.append(
                "CSP contains 'unsafe - eval' which may allow code injection"
            )
        if "'unsafe - inline'" in csp_header and "script-src" in csp_header:
            issues.append(
                "CSP allows 'unsafe - inline' scripts which reduces XSS protection"
            )
        if "data: " in csp_header and "script - src" in csp_header:
            issues.append(
                "CSP allows data: URLs in script - src which may be risky"
            )

        # Check for missing important directives
        if "object - src" not in csp_header:
            issues.append("CSP missing object - src directive")
        if "base - uri" not in csp_header:
            issues.append("CSP missing base - uri directive")

        return issues

    def _calculate_security_score(self, headers: Dict[str, str]) -> float:
        """Calculate security score based on headers."""
        score = 0.0
        max_score = 10.0

        # Basic security headers (6 points)
        security_headers = [
            "Content-Security-Policy",
            "X-Content-Type-Options",
            "X-Frame-Options",
            "X-XSS-Protection",
            "Referrer-Policy",
            "Strict-Transport-Security",
        ]
        for header in security_headers:
            if header in headers:
                score += 1.0

        # Child safety headers (2 points)
        if "X-Child-Safety-Enabled" in headers:
            score += 1.0
        if "X-COPPA-Compliant" in headers:
            score += 1.0

        # Additional security headers (2 points)
        additional_headers = [
            "X-Permitted-Cross-Domain-Policies",
            "X-Download-Options",
        ]
        for header in additional_headers:
            if header in headers:
                score += 1.0

        return min(score / max_score, 1.0)

    def get_security_report(self) -> Dict[str, Any]:
        """Get comprehensive security headers report."""
        return {
            "service_info": {
                "default_level": self.default_level.value,
                "available_levels": [level.value for level in SecurityLevel],
                "active_nonces": len(self.nonce_cache),
            },
            "configurations": {
                level.value: {
                    "child_safety_enabled": config.child_safety_enabled,
                    "coppa_compliant": config.coppa_compliant,
                    "hsts_max_age": config.hsts_max_age,
                    "frame_protection": config.x_frame_options,
                }
                for level, config in self.configurations.items()
            },
            "recommendations": [
                "Use CHILD_STRICT level for all child-facing interfaces",
                "Implement CSP nonces for better script security",
                "Enable HSTS preload for production domains",
                "Regularly review and update security configurations",
            ],
        }
