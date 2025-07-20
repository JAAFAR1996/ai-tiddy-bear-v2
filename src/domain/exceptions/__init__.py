"""Domain exception hierarchy for consistent error handling.
This module provides a structured exception hierarchy that maintains
clean architecture principles and enables consistent error handling.
"""

from .base_exceptions import (
    AuthorizationError,
    ConflictError,
    DomainException,
    NotFoundError,
    ValidationError,
)
from .child_exceptions import (
    ChildAccessDeniedError,
    ChildCreationError,
    ChildNotFoundError,
    InvalidChildAgeError,
)
from .security_exceptions import (
    AuthenticationError,
    ContentSafetyError,
    PermissionDeniedError,
    SecurityValidationError,
)

__all__ = [
    "AuthenticationError",
    "AuthorizationError",
    "ChildAccessDeniedError",
    "ChildCreationError",
    # Child-specific exceptions
    "ChildNotFoundError",
    "ConflictError",
    "ContentSafetyError",
    # Base exceptions
    "DomainException",
    "InvalidChildAgeError",
    "NotFoundError",
    "PermissionDeniedError",
    # Security exceptions
    "SecurityValidationError",
    "ValidationError",
]
