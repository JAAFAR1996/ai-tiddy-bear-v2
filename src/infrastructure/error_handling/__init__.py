"""Error handling package for AI Teddy Bear infrastructure."""

from src.common.exceptions import (
    AITeddyError,
    ServiceUnavailableError,
    InvalidInputError,
    TimeoutError,
    ConsentError,
    AgeRestrictionException,
    ChildSafetyException,
    ConfigurationError,
    DatabaseConnectionError,
    SecurityError,
    RateLimitExceededError,
    ResourceNotFoundError,
    StartupValidationException,
    ExternalServiceError,
    InfrastructureException,
    ConfigurationError,
    DatabaseConnectionError,
    SecurityError,
    RateLimitExceededError,
)

from .error_types import (
    ErrorType,
    ErrorSeverity,
    ErrorContext,
    BaseApplicationError,
    ExternalServiceError
)

# Import the actual decorators that exist
from .decorators import (
    handle_errors,
    retry_on_error,
    safe_execution,
    validate_result
)

# Import message functions that exist
from .messages import (
    get_error_message,
    ERROR_MESSAGES
)

__all__ = [
    # From application layer
    "AITeddyError",
    "ServiceUnavailableError", 
    "InvalidInputError",
    "TimeoutError",
    "ConsentError",
    "AgeRestrictionException",
    "ChildSafetyException",
    "ConfigurationError",
    "DatabaseConnectionError",
    "SecurityError",
    "RateLimitExceededError",
    "ResourceNotFoundError",
    "StartupValidationException",
    "ExternalServiceError",
    "InfrastructureException",
    "ConfigurationError",
    "DatabaseConnectionError",
    "SecurityError",
    "RateLimitExceededError",
    "handle_exception",
    "create_http_exception",
    "AITeddyErrorHandler",
    # Error types
    "ErrorType",
    "ErrorSeverity",
    "ErrorContext",
    "BaseApplicationError",
    "ExternalServiceError",
    # Actual decorators that exist
    "handle_errors",
    "retry_on_error",
    "safe_execution", 
    "validate_result",
    # Messages
    "get_error_message",
    "ERROR_MESSAGES"
]
