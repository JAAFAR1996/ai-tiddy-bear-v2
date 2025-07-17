"""
from typing import Dict, List, Optional, Union, Any
import warnings
from .validation_types import (
"""

"""Comprehensive Input Validation Service - Legacy Import Module
This module provides backward compatibility by re - exporting all validation
components from the new modular structure. Use the individual modules for
new code.
DEPRECATED: Use specific validator modules instead:
 - validation_types: ValidationResult, ValidationError, ValidationSeverity
 - child_safety_validator: ChildSafetyValidator
 - general_input_validator: GeneralInputValidator
 - comprehensive_validator: ComprehensiveValidator
"""

    ValidationResult,
    ValidationSeverity,
    ValidationError,
    PATTERNS,
    AGE_THRESHOLDS,
    LENGTH_LIMITS,
    SECURITY_PATTERNS)

# Re-export validators for backward compatibility
from .child_safety_validator import ChildSafetyValidator, get_child_safety_validator
from .general_input_validator import GeneralInputValidator, get_general_input_validator
from .comprehensive_validator import (
    ComprehensiveValidator,
    get_comprehensive_validator,
    validate_child_registration,
    validate_message_input,
    validate_file_upload)

# Issue deprecation warning
warnings.warn(
    "comprehensive_input_validator.py is deprecated. "
    "Use specific validator modules instead: "
    "child_safety_validator, general_input_validator, comprehensive_validator",
    DeprecationWarning,
    stacklevel=2)

# Backward compatibility factory functions
def create_comprehensive_validator(config: Optional[Dict[str, Any]] = None) -> ComprehensiveValidator:
    """
    DEPRECATED: Create comprehensive validator instance.
    Use get_comprehensive_validator() instead.
    """
    warnings.warn(
        "create_comprehensive_validator() is deprecated. Use get_comprehensive_validator() instead.",
        DeprecationWarning,
        stacklevel=2
    )
    return get_comprehensive_validator(config)

def create_child_safety_validator(config: Optional[Dict[str, Any]] = None) -> ChildSafetyValidator:
    """
    DEPRECATED: Create child safety validator instance.
    Use get_child_safety_validator() instead.
    """
    warnings.warn(
        "create_child_safety_validator() is deprecated. Use get_child_safety_validator() instead.",
        DeprecationWarning,
        stacklevel=2
    )
    return get_child_safety_validator(config)

def create_general_input_validator() -> GeneralInputValidator:
    """
    DEPRECATED: Create general input validator instance.
    Use get_general_input_validator() instead.
    """
    warnings.warn(
        "create_general_input_validator() is deprecated. Use get_general_input_validator() instead.",
        DeprecationWarning,
        stacklevel=2
    )
    return get_general_input_validator()

# Main validator instance for immediate use
_DEFAULT_VALIDATOR = None

def get_default_validator() -> ComprehensiveValidator:
    """Get default validator instance(singleton pattern)."""
    global _DEFAULT_VALIDATOR
    if _DEFAULT_VALIDATOR is None:
        _DEFAULT_VALIDATOR = get_comprehensive_validator()
    return _DEFAULT_VALIDATOR

# Convenient validation functions for backward compatibility
def validate_child_age(age: Union[int, str, None]) -> ValidationResult:
    """DEPRECATED: Use child_safety_validator.validate_child_age() instead."""
    warnings.warn(
        "validate_child_age() is deprecated. Use ChildSafetyValidator.validate_child_age() instead.",
        DeprecationWarning,
        stacklevel=2
    )
    validator = get_child_safety_validator()
    return validator.validate_child_age(age)

def validate_child_message(message: str, child_age: int = None) -> ValidationResult:
    """DEPRECATED: Use child_safety_validator.validate_child_message() instead."""
    warnings.warn(
        "validate_child_message() is deprecated. Use ChildSafetyValidator.validate_child_message() instead.",
        DeprecationWarning,
        stacklevel=2
    )
    validator = get_child_safety_validator()
    return validator.validate_child_message(message, child_age)

def validate_email(email: str, required: bool = True) -> ValidationResult:
    """DEPRECATED: Use general_input_validator.validate_email() instead."""
    warnings.warn(
        "validate_email() is deprecated. Use GeneralInputValidator.validate_email() instead.",
        DeprecationWarning,
        stacklevel=2
    )
    validator = get_general_input_validator()
    return validator.validate_email(email, required)

def validate_url(url: str, allowed_schemes: List[str] = None) -> ValidationResult:
    """DEPRECATED: Use general_input_validator.validate_url() instead."""
    warnings.warn(
        "validate_url() is deprecated. Use GeneralInputValidator.validate_url() instead.",
        DeprecationWarning,
        stacklevel=2
    )
    validator = get_general_input_validator()
    return validator.validate_url(url, allowed_schemes)

# Export all classes and functions for backward compatibility
__all__ = [
    # Types
    'ValidationResult',
    'ValidationSeverity',
    'ValidationError',
    
    # Validators
    'ChildSafetyValidator',
    'GeneralInputValidator',
    'ComprehensiveValidator',
    
    # Factory functions
    'get_child_safety_validator',
    'get_general_input_validator',
    'get_comprehensive_validator',
    'get_default_validator',
    
    # Deprecated factory functions
    'create_comprehensive_validator',
    'create_child_safety_validator',
    'create_general_input_validator',
    
    # Convenient functions
    'validate_child_registration',
    'validate_message_input',
    'validate_file_upload',
    
    # Deprecated convenient functions
    'validate_child_age',
    'validate_child_message',
    'validate_email',
    'validate_url',
    
    # Constants
    'PATTERNS',
    'AGE_THRESHOLDS',
    'LENGTH_LIMITS',
    'SECURITY_PATTERNS',
]