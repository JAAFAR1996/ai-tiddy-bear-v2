"""Comprehensive Input Validation Middleware for AI Teddy Bear Backend.
This module provides backwards compatibility imports from the new modular input validation system.
The implementation has been refactored into smaller, more maintainable modules."""

import logging
from .input_validation import (
    SecurityThreat,
    InputValidationResult,
    ComprehensiveInputValidator,
    get_input_validator,
    validate_user_input,
    validate_child_message,
    InputValidationMiddleware,
    create_input_validation_middleware)

from src.infrastructure.logging_config import get_logger
logger = get_logger(__name__, component="security")

# Export all the imported components for backwards compatibility
__all__ = [
    "SecurityThreat",
    "InputValidationResult",
    "ComprehensiveInputValidator",
    "get_input_validator",
    "validate_user_input",
    "validate_child_message",
    "InputValidationMiddleware",
    "create_input_validation_middleware"
]