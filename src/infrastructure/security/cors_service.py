from dataclasses import dataclass
from enum import Enum
from typing import Dict, Optional, Set
import re
import urllib.parse

from src.infrastructure.logging_config import get_logger

logger = get_logger(__name__, component="security")


class CORSPolicy(Enum):
    """CORS policy levels for different security requirements."""

    STRICT = "strict"  # Most restrictive - for child interactions
    MODERATE = "moderate"  # Balanced - for admin interfaces
    PERMISSIVE = "permissive"  # Least restrictive - for development


@dataclass
class CORSConfiguration:
    """CORS configuration with security - first defaults."""

    allowed_origins: Set[str]
    allowed_methods: Set[str]
    allowed_headers: Set[str]
    expose_headers: Set[str]
    allow_credentials: bool
    max_age: int
    policy_level: CORSPolicy

    def __post_init__(self):
        """Validate CORS configuration on initialization."""
        if "*" in self.allowed_origins and self.allow_credentials:
            raise ValueError("Cannot allow credentials with wildcard origins")


class CORSSecurityService:
    """
    Enterprise - grade CORS security service for child - safe applications.
    Features:
    - Age - appropriate CORS policies
    - Origin validation and sanitization
    - Security header enforcement
    - Audit logging for CORS violations
    - Dynamic policy adjustment
    """

    def __init__(self, default_policy: CORSPolicy = CORSPolicy.STRICT) -> None:
        """Initialize CORS security service."""
        self.default_policy = default_policy
        self.configurations = self._initialize_cors_configurations()
        self.origin_cache: Dict[str, bool] = {}
        self.violation_count: Dict[str, int] = {}
        self.max_cache_size = 1000

        logger.info(
            f"CORS security service initialized with {default_policy.value} policy"
        )

    def _initialize_cors_configurations(
        self,
    ) -> Dict[CORSPolicy, CORSConfiguration]:
        """Initialize predefined CORS configurations."""
        return {
            CORSPolicy.STRICT: CORSConfiguration(
                allowed_origins={
                    "https://ai-teddy.com",
                    "https://www.ai-teddy.com",
                    "https://child.ai-teddy.com",
                },
                allowed_methods={"GET", "POST"},
                allowed_headers={
                    "Content-Type",
                    "Authorization",
                    "X-Requested-With",
                    "X-Child-ID",
                    "X-Parent-Consent",
                },
                expose_headers={
                    "X-RateLimit-Remaining",
                    "X-Content-Safety-Score",
                },
                allow_credentials=True,
                max_age=300,  # 5 minutes for strict policy
                policy_level=CORSPolicy.STRICT,
            ),
            CORSPolicy.MODERATE: CORSConfiguration(
                allowed_origins={
                    "https://ai-teddy.com",
                    "https://admin.ai-teddy.com",
                    "https://parent.ai-teddy.com",
                    "https://localhost:3000",  # Development
                    "https://localhost:8080",
                },
                allowed_methods={"GET", "POST", "PUT", "DELETE", "OPTIONS"},
                allowed_headers={
                    "Content-Type",
                    "Authorization",
                    "X-Requested-With",
                    "X-CSRF-Token",
                    "X-Admin-Token",
                },
                expose_headers={
                    "X-RateLimit-Remaining",
                    "X-Total-Count",
                    "X-API-Version",
                },
                allow_credentials=True,
                max_age=3600,  # 1 hour
                policy_level=CORSPolicy.MODERATE,
            ),
            CORSPolicy.PERMISSIVE: CORSConfiguration(
                allowed_origins={
                    "http://localhost:3000",
                    "http://localhost:8080",
                    "http://127.0.0.1:3000",
                    "https://localhost:3000",
                },
                allowed_methods={
                    "GET",
                    "POST",
                    "PUT",
                    "DELETE",
                    "OPTIONS",
                    "PATCH",
                },
                allowed_headers={
                    "Content-Type",
                    "Authorization",
                    "X-Requested-With",
                    "Accept",
                    "Origin",
                    "Cache-Control",
                },
                expose_headers={"X-RateLimit-Remaining", "X-Debug-Info"},
                allow_credentials=True,
                max_age=86400,  # 24 hours - development only
                policy_level=CORSPolicy.PERMISSIVE,
            ),
        }

    def validate_origin(
        self, origin: Optional[str], policy: Optional[CORSPolicy] = None
    ) -> Dict[str, any]:
        """
        Validate if origin is allowed for CORS requests.
        Args:
            origin: Request origin header
            policy: CORS policy to apply(defaults to service default)
        Returns:
            Dict with validation result and CORS headers
        """
        if not origin:
            logger.warning("Missing origin header in CORS request")
            return {
                "allowed": False,
                "reason": "Missing origin header",
                "headers": self._get_cors_headers_for_error(),
            }

        # Use specified policy or default
        policy = policy or self.default_policy
        config = self.configurations[policy]

        # Check cache first
        cache_key = f"{origin}:{policy.value}"
        if cache_key in self.origin_cache:
            is_allowed = self.origin_cache[cache_key]
            if is_allowed:
                return {
                    "allowed": True,
                    "origin": origin,
                    "headers": self._generate_cors_headers(origin, config),
                    "cached": True,
                }

        # Validate origin format and security
        validation_result = self._validate_origin_security(origin)
        if not validation_result["secure"]:
            self._log_cors_violation(origin, validation_result["reason"])
            return {
                "allowed": False,
                "reason": validation_result["reason"],
                "headers": self._get_cors_headers_for_error(),
                "security_violation": True,
            }

        # Check against allowed origins
        is_allowed = self._is_origin_allowed(origin, config)

        # Update cache
        self._update_origin_cache(cache_key, is_allowed)

        if is_allowed:
            headers = self._generate_cors_headers(origin, config)
            logger.debug(f"CORS request allowed for origin: {origin}")
            return {
                "allowed": True,
                "origin": origin,
                "headers": headers,
                "policy": policy.value,
            }
        else:
            self._log_cors_violation(origin, "Origin not in allowed list")
            return {
                "allowed": False,
                "reason": "Origin not allowed",
                "headers": self._get_cors_headers_for_error(),
            }

    def handle_preflight_request(
        self,
        origin: Optional[str],
        method: Optional[str],
        headers: Optional[str],
        policy: Optional[CORSPolicy] = None,
    ) -> Dict[str, any]:
        """
        Handle CORS preflight OPTIONS requests.
        Args:
            origin: Request origin
            method: Requested method via Access - Control - Request - Method
            headers: Requested headers via Access - Control - Request - Headers
            policy: CORS policy to apply
        Returns:
            Dict with preflight validation result and headers
        """
        # First validate the origin
        origin_validation = self.validate_origin(origin, policy)
        if not origin_validation["allowed"]:
            return origin_validation

        policy = policy or self.default_policy
        config = self.configurations[policy]

        # Validate requested method
        if method and method.upper() not in config.allowed_methods:
            logger.warning(
                f"CORS preflight: Method {method} not allowed for {origin}"
            )
            return {
                "allowed": False,
                "reason": f"Method {method} not allowed",
                "headers": self._get_cors_headers_for_error(),
            }

        # Validate requested headers
        if headers:
            requested_headers = {h.strip() for h in headers.split(",")}
            if not requested_headers.issubset(config.allowed_headers):
                forbidden_headers = requested_headers - config.allowed_headers
                logger.warning(
                    f"CORS preflight: Headers {forbidden_headers} not allowed for {origin}"
                )
                return {
                    "allowed": False,
                    "reason": f"Headers not allowed: {', '.join(forbidden_headers)}",
                    "headers": self._get_cors_headers_for_error(),
                }

        # Generate preflight response headers
        preflight_headers = self._generate_preflight_headers(origin, config)
        logger.debug(
            f"CORS preflight approved for {origin}: {method} with headers {headers}"
        )
        return {
            "allowed": True,
            "origin": origin,
            "method": method,
            "headers": preflight_headers,
            "policy": policy.value,
        }

    def get_security_headers(
        self, policy: Optional[CORSPolicy] = None
    ) -> Dict[str, str]:
        """
        Get additional security headers for CORS responses.
        Args:
            policy: CORS policy level
        Returns:
            Dict of security headers
        """
        policy = policy or self.default_policy

        # Base security headers for all policies
        headers = {
            "X-Content-Type-Options": "nosniff",
            "X-Frame-Options": "DENY",
            "X-XSS-Protection": "1; mode=block",
            "Referrer-Policy": "strict-origin-when-cross-origin",
            "Content-Security-Policy": self._get_csp_header(policy),
        }

        # Add stricter headers for child safety
        if policy == CORSPolicy.STRICT:
            headers.update(
                {
                    "Strict-Transport-Security": "max-age=31536000; includeSubDomains; preload",
                    "X-Child-Safety": "enabled",
                    "X-Content-Safety-Policy": "child-safe",
                }
            )

        return headers

    def _validate_origin_security(self, origin: str) -> Dict[str, any]:
        """Validate origin for security issues."""
        try:
            parsed = urllib.parse.urlparse(origin)

            # Check for basic URL structure
            if not parsed.scheme or not parsed.netloc:
                return {"secure": False, "reason": "Invalid origin format"}

            # Only allow HTTPS in production (except localhost)
            if parsed.scheme not in ["https", "http"]:
                return {"secure": False, "reason": "Invalid scheme"}

            # Check for localhost exception
            is_localhost = parsed.netloc.startswith(
                ("localhost", "127.0.0.1", "0.0.0.0")
            )
            if parsed.scheme == "http" and not is_localhost:
                return {
                    "secure": False,
                    "reason": "HTTP not allowed for non-localhost",
                }

            # Check for suspicious characters
            if re.search(r'[<>"\'\x00-\x1f\x7f-\x9f]', origin):
                return {
                    "secure": False,
                    "reason": "Suspicious characters in origin",
                }

            # Check domain format
            if not re.match(r"^[a-zA-Z0-9.-]+$", parsed.netloc.split(":")[0]):
                return {"secure": False, "reason": "Invalid domain format"}

            return {"secure": True}
        except Exception as e:
            logger.error(f"Error validating origin security: {e}")
            return {"secure": False, "reason": "Origin validation error"}

    def _is_origin_allowed(
        self, origin: str, config: CORSConfiguration
    ) -> bool:
        """Check if origin is in allowed list."""
        # Exact match first
        if origin in config.allowed_origins:
            return True

        # Check for wildcard patterns (if any)
        parsed_origin = urllib.parse.urlparse(origin)
        for allowed in config.allowed_origins:
            if allowed.startswith("*."):
                # Subdomain wildcard matching
                allowed_domain = allowed[2:]  # Remove *.
                if (
                    parsed_origin.netloc.endswith(f".{allowed_domain}")
                    or parsed_origin.netloc == allowed_domain
                ):
                    return True

        return False

    def _generate_cors_headers(
        self, origin: str, config: CORSConfiguration
    ) -> Dict[str, str]:
        """Generate CORS response headers."""
        headers = {
            "Access-Control-Allow-Origin": origin,
            "Access-Control-Allow-Methods": ", ".join(
                sorted(config.allowed_methods)
            ),
            "Access-Control-Allow-Headers": ", ".join(
                sorted(config.allowed_headers)
            ),
            "Access-Control-Max-Age": str(config.max_age),
        }

        if config.expose_headers:
            headers["Access-Control-Expose-Headers"] = ", ".join(
                sorted(config.expose_headers)
            )

        if config.allow_credentials:
            headers["Access-Control-Allow-Credentials"] = "true"

        return headers

    def _generate_preflight_headers(
        self, origin: str, config: CORSConfiguration
    ) -> Dict[str, str]:
        """Generate preflight response headers."""
        headers = self._generate_cors_headers(origin, config)

        # Additional preflight-specific headers
        headers.update(
            {
                "Vary": "Origin, Access-Control-Request-Method, Access-Control-Request-Headers",
                "Cache-Control": f"max-age={config.max_age}",
            }
        )

        return headers

    def _get_cors_headers_for_error(self) -> Dict[str, str]:
        """Get minimal CORS headers for error responses."""
        return {
            "Access-Control-Allow-Origin": "",
            "Access-Control-Allow-Methods": "",
            "Access-Control-Allow-Headers": "",
            "Vary": "Origin",
        }

    def _get_csp_header(self, policy: CORSPolicy) -> str:
        """Get Content Security Policy header based on CORS policy."""
        if policy == CORSPolicy.STRICT:
            return (
                "default-src 'self'; "
                "script-src 'self' 'unsafe-inline'; "
                "style-src 'self' 'unsafe-inline'; "
                "img-src 'self' data: https:; "
                "connect-src 'self'; "
                "frame-ancestors 'none';"
            )
        elif policy == CORSPolicy.MODERATE:
            return (
                "default-src 'self'; "
                "script-src 'self' 'unsafe-inline' 'unsafe-eval'; "
                "style-src 'self' 'unsafe-inline'; "
                "img-src 'self' data: https:; "
                "connect-src 'self' https:;"
            )
        else:  # PERMISSIVE
            return (
                "default-src 'self'; "
                "script-src 'self' 'unsafe-inline' 'unsafe-eval'; "
                "style-src 'self' 'unsafe-inline'; "
                "img-src 'self' data: https: http:; "
                "connect-src 'self' https: http: ws: wss:;"
            )

    def _log_cors_violation(self, origin: str, reason: str) -> None:
        """Log CORS violation for security monitoring."""
        # Track violation count
        self.violation_count[origin] = self.violation_count.get(origin, 0) + 1
        logger.warning(
            f"CORS violation from {origin}: {reason} (total: {self.violation_count[origin]})"
        )

        # Alert on repeated violations
        if self.violation_count[origin] >= 5:
            logger.error(
                f"Repeated CORS violations from {origin} - possible attack"
            )

    def _update_origin_cache(self, cache_key: str, is_allowed: bool) -> None:
        """Update origin validation cache."""
        if len(self.origin_cache) >= self.max_cache_size:
            # Remove oldest entries
            oldest_keys = list(self.origin_cache.keys())[:100]
            for key in oldest_keys:
                del self.origin_cache[key]

        self.origin_cache[cache_key] = is_allowed

    def get_cors_statistics(self) -> Dict[str, any]:
        """Get CORS service statistics for monitoring."""
        return {
            "default_policy": self.default_policy.value,
            "cached_origins": len(self.origin_cache),
            "violation_count": sum(self.violation_count.values()),
            "unique_violating_origins": len(self.violation_count),
            "top_violating_origins": sorted(
                self.violation_count.items(), key=lambda x: x[1], reverse=True
            )[:5],
        }

    def add_allowed_origin(self, origin: str, policy: CORSPolicy) -> bool:
        """
        Dynamically add an allowed origin to a policy.
        Args:
            origin: Origin to add
            policy: Policy to modify
        Returns:
            True if successfully added
        """
        try:
            # Validate origin first
            validation = self._validate_origin_security(origin)
            if not validation["secure"]:
                logger.error(f"Cannot add insecure origin: {origin}")
                return False

            # Add to configuration
            self.configurations[policy].allowed_origins.add(origin)

            # Clear related cache entries
            cache_keys_to_remove = [
                key
                for key in self.origin_cache.keys()
                if key.startswith(f"{origin}:")
            ]
            for key in cache_keys_to_remove:
                del self.origin_cache[key]

            logger.info(f"Added origin {origin} to {policy.value} policy")
            return True
        except Exception as e:
            logger.error(f"Error adding origin {origin}: {e}")
            return False

    def remove_allowed_origin(self, origin: str, policy: CORSPolicy) -> bool:
        """
        Remove an allowed origin from a policy.
        Args:
            origin: Origin to remove
            policy: Policy to modify
        Returns:
            True if successfully removed
        """
        try:
            # Remove from configuration
            self.configurations[policy].allowed_origins.discard(origin)

            # Clear related cache entries
            cache_keys_to_remove = [
                key
                for key in self.origin_cache.keys()
                if key.startswith(f"{origin}:")
            ]
            for key in cache_keys_to_remove:
                del self.origin_cache[key]

            logger.info(f"Removed origin {origin} from {policy.value} policy")
            return True
        except Exception as e:
            logger.error(f"Error removing origin {origin}: {e}")
            return False
