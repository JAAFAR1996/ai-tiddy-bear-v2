"""Error handling package for AI Teddy Bear infrastructure."""

# Import from application layer
from src.application.exceptions import (
    AITeddyError,
    ServiceUnavailableError,
    InvalidInputError,
    TimeoutError
)

# Import from local modules
from .exceptions import (
    BaseInfrastructureException,
    ConfigurationError,
    DatabaseConnectionError,
    SecurityError,
    RateLimitExceededError,
    handle_exception,
    create_http_exception,
    AITeddyErrorHandler
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
    # From infrastructure
    "BaseInfrastructureException",
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
