from typing import Optional
from uuid import uuid4
import os
from fastapi import HTTPException, status


from src.infrastructure.logging_config import get_logger

logger = get_logger(__name__, component="security")


class SecureErrorHandler:
    """Handles errors securely by sanitizing sensitive information"""

    def __init__(self):
        self.environment = os.getenv("ENVIRONMENT", "development").lower()
        self.is_production = self.environment == "production"

    def create_safe_error_response(
        self,
        error: Exception,
        status_code: int = status.HTTP_500_INTERNAL_SERVER_ERROR,
        default_message: str = "An error occurred while processing your request",
        user_context: Optional[str] = None,
    ) -> HTTPException:
        """
        Create a secure error response that doesn't leak sensitive information.
        Args:
            error: The original exception
            status_code: HTTP status code to return
            default_message: Safe message to return to users
            user_context: Additional context for user (safe to expose)
        Returns:
            HTTPException with sanitized error message
        """
        # Generate unique error ID for tracking
        error_id = str(uuid4())[:8]

        # Log the full error details for debugging (internal only)
        logger.error(
            f"Error ID {error_id}: {type(error).__name__}: {str(error)}",
            exc_info=True,
            extra={
                "error_id": error_id,
                "error_type": type(error).__name__,
                "status_code": status_code,
                "user_context": user_context,
            },
        )

        # Determine what to expose to the user
        if self.is_production:
            # Production: Only expose generic messages
            detail = self._get_production_safe_message(
                status_code, default_message, error_id
            )
        else:
            # Development: Include more detail for debugging
            detail = self._get_development_message(
                error, default_message, error_id
            )

        # Add user context if provided
        if user_context:
            detail = f"{detail}. Context: {user_context}"

        return HTTPException(status_code=status_code, detail=detail)

    def _get_production_safe_message(
        self, status_code: int, default_message: str, error_id: str
    ) -> str:
        """Get production-safe error message"""
        safe_messages = {
            400: "Invalid request parameters",
            401: "Authentication required",
            403: "Access denied",
            404: "Resource not found",
            413: "Request too large",
            422: "Invalid input data",
            429: "Too many requests",
            500: "Internal server error",
            502: "Service temporarily unavailable",
            503: "Service temporarily unavailable",
        }
        base_message = safe_messages.get(status_code, default_message)
        return f"{base_message}. Error ID: {error_id}"

    def _get_development_message(
        self, error: Exception, default_message: str, error_id: str
    ) -> str:
        """Get development error message with more detail"""
        error_type = type(error).__name__
        error_msg = str(error)

        # Still sanitize sensitive patterns in development
        sanitized_msg = self._sanitize_sensitive_info(error_msg)

        return f"{default_message}. Error ID: {error_id}. Type: {error_type}. Details: {sanitized_msg}"

    def _sanitize_sensitive_info(self, message: str) -> str:
        """Remove potentially sensitive information from error messages"""
        import re

        # Patterns to redact
        patterns = [
            # Database connection strings
            (
                r"postgresql: // [ ^ /]+/[^\"\\s]+",
                "postgresql://[REDACTED]/[REDACTED]",
            ),
            (r"sqlite:///[^\"\\s]+", "sqlite: // /[REDACTED]"),
            # API keys and tokens
            (r"sk-[a-zA-Z0-9]{48}", "sk-[REDACTED]"),
            (r"Bearer [a-zA-Z0-9._-]+", "Bearer [REDACTED]"),
            # File paths
            (r"/[a-zA-Z0-9/_.-] +\\.py", "/[REDACTED].py"),
            (r"[A-Z]: \\\\[a-zA-Z0-9\\\\._-]+", "[REDACTED_PATH]"),
            # Email addresses
            (
                r"[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-] +\\.[a-zA-Z]{2, }",
                "[REDACTED_EMAIL]",
            ),
            # IP addresses
            (r"\\b(?: \\d{1, 3}\\.){3}\\d{1, 3}\\b", "[REDACTED_IP]"),
            # UUIDs
            (
                r"[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}",
                "[REDACTED_UUID]",
            ),
        ]

        sanitized = message
        for pattern, replacement in patterns:
            sanitized = re.sub(
                pattern, replacement, sanitized, flags=re.IGNORECASE
            )

        return sanitized

    def handle_database_error(self, error: Exception) -> HTTPException:
        """Handle database-specific errors securely"""
        return self.create_safe_error_response(
            error,
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            default_message="Database operation failed",
        )

    def handle_authentication_error(self, error: Exception) -> HTTPException:
        """Handle authentication errors securely"""
        return self.create_safe_error_response(
            error,
            status_code=status.HTTP_401_UNAUTHORIZED,
            default_message="Authentication failed",
        )

    def handle_authorization_error(self, error: Exception) -> HTTPException:
        """Handle authorization errors securely"""
        return self.create_safe_error_response(
            error,
            status_code=status.HTTP_403_FORBIDDEN,
            default_message="Access denied",
        )

    def handle_validation_error(self, error: Exception) -> HTTPException:
        """Handle input validation errors securely"""
        return self.create_safe_error_response(
            error,
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            default_message="Invalid input data",
        )

    def handle_file_upload_error(self, error: Exception) -> HTTPException:
        """Handle file upload errors securely"""
        return self.create_safe_error_response(
            error,
            status_code=status.HTTP_400_BAD_REQUEST,
            default_message="File upload failed",
        )

    def handle_external_service_error(self, error: Exception) -> HTTPException:
        """Handle external service errors securely"""
        return self.create_safe_error_response(
            error,
            status_code=status.HTTP_502_BAD_GATEWAY,
            default_message="External service temporarily unavailable",
        )


# Global instance for easy access
_error_handler = SecureErrorHandler()


def get_secure_error_handler() -> SecureErrorHandler:
    """Get the global secure error handler instance"""
    return _error_handler


def create_safe_error(
    error: Exception,
    status_code: int = status.HTTP_500_INTERNAL_SERVER_ERROR,
    default_message: str = "An error occurred",
    user_context: Optional[str] = None,
) -> HTTPException:
    """
    Convenience function to create a safe error response.
    Usage:
        try:
            # some operation
        except Exception as e:
            raise create_safe_error(e, 400, "Operation failed")
    """
    return _error_handler.create_safe_error_response(
        error, status_code, default_message, user_context
    )
