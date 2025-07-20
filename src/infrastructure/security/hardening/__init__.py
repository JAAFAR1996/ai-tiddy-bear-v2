"""Security Hardening Components for AI Teddy Bear
Comprehensive security hardening package with enterprise-grade protections
"""

from .csrf_protection import (
    CSRFConfig,
    CSRFMiddleware,
    CSRFProtection,
    CSRFTokenManager,
    csrf_protect,
    get_csrf_protection,
    init_csrf_protection,
)
from .input_validation import (
    InputSanitizer,
    InputValidationConfig,
    InputValidationMiddleware,
    ValidationRule,
    ValidationSeverity,
    create_input_validation_middleware,
)
from ..rate_limiter.core import (
    ChildSafetyRateLimiter,
    RateLimitConfig,
    RateLimitResult,
    RedisRateLimiter,
    get_child_safety_limiter,
    get_rate_limiter,
)
from .security_headers import (
    SecurityHeadersConfig,
    SecurityHeadersMiddleware,
    create_security_headers_middleware,
    get_security_headers_config,
    init_security_headers,
)
# استيراد SecurityValidator من الملف الصحيح
from .security_validator import (
    SecurityValidator,
    SecurityContext,
    ValidationResult,
    SecurityLevel,
    ComplianceStandard,
)

__all__ = [
    # Rate Limiting
    "RedisRateLimiter",
    "ChildSafetyRateLimiter",
    "RateLimitConfig",
    "RateLimitResult",
    "get_rate_limiter",
    "get_child_safety_limiter",
    # CSRF Protection
    "CSRFProtection",
    "CSRFTokenManager",
    "CSRFConfig",
    "CSRFMiddleware",
    "get_csrf_protection",
    "init_csrf_protection",
    "csrf_protect",
    # Security Headers
    "SecurityHeadersMiddleware",
    "SecurityHeadersConfig",
    "get_security_headers_config",
    "init_security_headers",
    "create_security_headers_middleware",
    # Security Validator
    "SecurityValidator",
    "SecurityContext",
    "ValidationResult",
    "SecurityLevel",
    "ComplianceStandard",
    # Input Validation
    "InputValidationMiddleware",
    "InputSanitizer",
    "InputValidationConfig",
    "ValidationRule",
    "ValidationSeverity",
    "create_input_validation_middleware",
]
# Package version
__version__ = "1.0.0"