"""Domain exception hierarchy for consistent error handling.
This module provides a structured exception hierarchy that maintains
clean architecture principles and enables consistent error handling."""

from .base_exceptions import (
    DomainException,
    ValidationError,
    AuthorizationError,
    NotFoundError,
    ConflictError)

from .child_exceptions import (
    ChildNotFoundError,
    InvalidChildAgeError,
    ChildAccessDeniedError,
    ChildCreationError)

from .security_exceptions import (
    SecurityValidationError,
    ContentSafetyError,
    AuthenticationError,
    PermissionDeniedError)

__all__ = [
    # Base exceptions
    'DomainException',
    'ValidationError',
    'AuthorizationError',
    'NotFoundError',
    'ConflictError',
    # Child-specific exceptions
    'ChildNotFoundError',
    'InvalidChildAgeError',
    'ChildAccessDeniedError',
    'ChildCreationError',
    # Security exceptions
    'SecurityValidationError',
    'ContentSafetyError',
    'AuthenticationError',
    'PermissionDeniedError'
]