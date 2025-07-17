"""Standardized error handling for AI Teddy Bear backend."""
from .exceptions import (
    AITeddyError,
    ValidationError,
    AuthenticationError,
    AuthorizationError,
    NotFoundError,
    ConflictError,
    ExternalServiceError,
    RateLimitError,
    ChildSafetyError,
)
from .handlers import (
    ErrorHandler,
    get_error_handler,
    standardize_error_response,
)

__all__ = [
    "AITeddyError",
    "ValidationError",
    "AuthenticationError",
    "AuthorizationError",
    "NotFoundError",
    "ConflictError",
    "ExternalServiceError",
    "RateLimitError",
    "ChildSafetyError",
    "ErrorHandler",
    "get_error_handler",
    "standardize_error_response",
]