"""Modular input validation system for AI Teddy Bear backend.
This package provides comprehensive input validation with:
 - Security threat detection (SQL injection, XSS, path traversal, etc.)
 - Child safety content filtering
 - PII detection and protection
 - FastAPI middleware integration
"""

from .core import InputValidationResult, SecurityThreat
from .middleware import InputValidationMiddleware, create_input_validation_middleware
from .validator import (
    ComprehensiveInputValidator,
    get_input_validator,
    validate_child_message,
    validate_user_input,
)

__all__ = [
    "ComprehensiveInputValidator",
    "InputValidationMiddleware",
    "InputValidationResult",
    "SecurityThreat",
    "create_input_validation_middleware",
    "get_input_validator",
    "validate_child_message",
    "validate_user_input",
]
