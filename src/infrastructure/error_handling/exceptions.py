"""Exception handling for AI Teddy Bear infrastructure."""

from typing import Any, Dict, Optional
from fastapi import HTTPException, status


class BaseInfrastructureException(Exception):
    """Base exception for infrastructure layer."""
    
    def __init__(self, message: str, details: Optional[Dict[str, Any]] = None):
        self.message = message
        self.details = details or {}
        super().__init__(self.message)


class ConfigurationError(BaseInfrastructureException):
    """Configuration related errors."""
    pass


class DatabaseConnectionError(BaseInfrastructureException):
    """Database connection errors."""
    pass


class SecurityError(BaseInfrastructureException):
    """Security related errors."""
    pass


class RateLimitExceededError(BaseInfrastructureException):
    """Rate limit exceeded error."""
    pass


# HTTP Exception helpers
def create_http_exception(
    status_code: int,
    message: str,
    details: Optional[Dict[str, Any]] = None
) -> HTTPException:
    """Create HTTP exception with details."""
    return HTTPException(
        status_code=status_code,
        detail={
            "message": message,
            "details": details or {},
            "child_safe": True
        }
    )


def handle_exception(exception: Exception) -> HTTPException:
    """Handle and convert exceptions to HTTP responses."""
    if isinstance(exception, BaseInfrastructureException):
        return create_http_exception(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            message=exception.message,
            details=exception.details
        )
    
    # Generic exception handling
    return create_http_exception(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        message="An unexpected error occurred",
        details={"type": type(exception).__name__}
    )


class AITeddyErrorHandler:
    """Handler for AITeddyError and related exceptions."""
    
    @staticmethod
    def handle_authentication_error(message: str = "Authentication required"):
        """Handle authentication errors."""
        from src.application.exceptions import AITeddyError
        return AITeddyError(f"Auth Error: {message}")
    
    @staticmethod
    def handle_authorization_error(message: str = "Access denied"):
        """Handle authorization errors.""" 
        from src.application.exceptions import AITeddyError
        return AITeddyError(f"Auth Error: {message}")
    
    @staticmethod
    def handle_validation_error(message: str = "Invalid input"):
        """Handle validation errors."""
        from src.application.exceptions import InvalidInputError
        return InvalidInputError(message)
    
    @staticmethod
    def handle_not_found_error(message: str = "Resource not found"):
        """Handle not found errors."""
        from src.application.exceptions import AITeddyError
        return AITeddyError(f"Not Found: {message}")
    
    @staticmethod
    def handle_internal_error(message: str = "Internal server error"):
        """Handle internal server errors."""
        from src.application.exceptions import AITeddyError
        return AITeddyError(f"Internal Error: {message}")
