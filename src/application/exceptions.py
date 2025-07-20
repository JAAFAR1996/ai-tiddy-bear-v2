"""Custom exceptions for the application layer."""
from typing import Any
class AITeddyError(Exception):
    """Base exception for all AI Teddy Bear specific errors."""

    def __init__(
        self,
        message: str,
        error_code: str | None = None,
        details: dict[str, Any] | None = None,
        http_status: int = 500,
    ):
        super().__init__(message)
        self.message = message
        self.error_code = error_code or self.__class__.__name__
        self.details = details or {}
        self.http_status = http_status

class ServiceUnavailableError(AITeddyError):
    """Raised when a required service (e.g., AI provider, DB) is unavailable."""

    def __init__(self, message: str = "Service temporarily unavailable", **kwargs):
        super().__init__(
            message=message,
            error_code="SERVICE_UNAVAILABLE",
            http_status=503,  # 503 Service Unavailable
            **kwargs,
        )

class InvalidInputError(AITeddyError):
    """Raised when input provided to a service is invalid."""

    def __init__(self, message: str = "Invalid input", **kwargs):
        super().__init__(
            message=message,
            error_code="INVALID_INPUT",
            http_status=400,
            **kwargs,
        )

class TimeoutError(AITeddyError):
    """Raised when an operation times out (e.g., request to external service)."""

    def __init__(self, message: str = "Request timed out", **kwargs):
        super().__init__(
            message=message,
            error_code="TIMEOUT",
            http_status=504,  # 504 Gateway Timeout
            **kwargs,
        ) 
class ConsentError(Exception):
    """
    Raised when a user's consent is missing or invalid.
    Used in AI response generation and consent validation flows.
    """
    def __init__(self, message="Consent is required", *args, **kwargs):
        super().__init__(message, *args, **kwargs)
