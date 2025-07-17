"""Standardized error handling for AI Teddy Bear backend."""

from .exceptions import (
    AITeddyError,
    AuthenticationError,
    AuthorizationError,
    ChildSafetyError,
    ConflictError,
    ExternalServiceError,
    NotFoundError,
    RateLimitError,
    ValidationError,
)
from .handlers import (
    ErrorHandler,
    get_error_handler,
    standardize_error_response,
)

__all__ = [
    "AITeddyError",
    "AuthenticationError",
    "AuthorizationError",
    "ChildSafetyError",
    "ConflictError",
    "ErrorHandler",
    "ExternalServiceError",
    "NotFoundError",
    "RateLimitError",
    "ValidationError",
    "get_error_handler",
    "standardize_error_response",
]
