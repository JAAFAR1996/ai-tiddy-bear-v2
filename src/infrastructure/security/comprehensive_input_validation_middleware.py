"""Comprehensive Input Validation Middleware for AI Teddy Bear Backend.
This module provides backwards compatibility imports from the new modular input validation system.
The implementation has been refactored into smaller, more maintainable modules.
"""

from src.infrastructure.logging_config import get_logger

from .input_validation import (
    ComprehensiveInputValidator,
    InputValidationMiddleware,
    InputValidationResult,
    SecurityThreat,
    create_input_validation_middleware,
    get_input_validator,
    validate_child_message,
    validate_user_input,
)

logger = get_logger(__name__, component="security")

# Export all the imported components for backwards compatibility
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
