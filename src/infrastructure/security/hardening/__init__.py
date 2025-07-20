"""Security Hardening Package
Collection of security hardening measures for the application.
Note: This module is currently not in use but kept for future implementation.
"""

# CSRF Protection
from .csrf_protection import (
    CSRFConfig,
    CSRFTokenManager,
    CSRFProtection,
    CSRFMiddleware,
    get_csrf_protection,
    init_csrf_protection,
    csrf_protect,
)

# Input Validation components
from .validation import (
    InputSanitizer,
    InputValidationConfig,
    ValidationRule,
    ValidationSeverity,
)

__all__ = [
    # CSRF Protection
    "CSRFConfig",
    "CSRFTokenManager",
    "CSRFProtection",
    "CSRFMiddleware",
    "get_csrf_protection",
    "init_csrf_protection",
    "csrf_protect",
    # Input Validation
    "InputSanitizer",
    "InputValidationConfig",
    "ValidationRule",
    "ValidationSeverity",
]

# Package version
__version__ = "1.0.0"
