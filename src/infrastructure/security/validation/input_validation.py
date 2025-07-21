import warnings

from src.infrastructure.security.validation import (
    InputSanitizer,
    InputValidationConfig,
    InputValidationMiddleware,
    ValidationRule,
    ValidationSeverity,
    create_input_validation_middleware,
)

# Re-export for backward compatibility
__all__ = [
    "InputSanitizer",
    "InputValidationConfig",
    "InputValidationMiddleware",
    "ValidationRule",
    "ValidationSeverity",
    "create_input_validation_middleware",
]
# Deprecation warning for direct imports
warnings.warn(
    "Importing from input_validation.py is deprecated. "
    "Please import from src.infrastructure.security.validation instead.",
    DeprecationWarning,
    stacklevel=2,
)
# Implements pattern-based validation, content filtering, and sanitization
# Provides special protections for child users with COPPA compliance
