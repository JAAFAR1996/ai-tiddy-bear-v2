"""
from datetime import datetime
from typing import Dict, Any, Optional, Union
import logging
import traceback
from .exceptions import AITeddyError

"""Error handling utilities and standardized response formatting."""
from src.infrastructure.logging_config import get_logger

logger = get_logger(__name__, component="infrastructure")

class ErrorHandler:
    """Centralized error handling and response formatting."""
    def __init__(self, log_errors: bool = True, include_details: bool = False):
        """
        Initialize error handler.

        Args:
            log_errors: Whether to log errors automatically
            include_details: Whether to include detailed error info in responses
        """
        self.log_errors = log_errors
        self.include_details = include_details

    def handle_error(
        self,
        error: Exception,
        context: Optional[Dict[str, Any]] = None,
        user_id: Optional[str] = None,
        child_id: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Handle an error and return a standardized response.

        Args:
            error: The exception that occurred
            context: Additional context information
            user_id: ID of the user (for logging)
            child_id: ID of the child (for logging, will be anonymized)

        Returns:
            Standardized error response dictionary
        """
        # Log the error if enabled
        if self.log_errors:
            self._log_error(error, context, user_id, child_id)

        # Create standardized response
        if isinstance(error, AITeddyError):
            return self._handle_aiteddy_error(error)
        else:
            return self._handle_generic_error(error)

    def _handle_aiteddy_error(self, error: AITeddyError) -> Dict[str, Any]:
        """Handle AI Teddy specific errors."""
        response = {
            "error": True,
            "error_code": error.error_code,
            "message": error.message,
            "timestamp": datetime.utcnow().isoformat(),
            "http_status": error.http_status
        }
        if self.include_details and error.details:
            response["details"] = error.details
        return response

    def _handle_generic_error(self, error: Exception) -> Dict[str, Any]:
        """Handle generic, unexpected errors."""
        response = {
            "error": True,
            "error_code": "INTERNAL_SERVER_ERROR",
            "message": "An unexpected error occurred. Our team has been notified.",
            "timestamp": datetime.utcnow().isoformat(),
            "http_status": 500
        }
        if self.include_details:
            response["details"] = {
                "error_type": type(error).__name__,
                "error_message": str(error)
            }
        return response

    def _log_error(
        self,
        error: Exception,
        context: Optional[Dict[str, Any]],
        user_id: Optional[str],
        child_id: Optional[str]
    ):
        """Log error details."""
        log_level = "error" if not isinstance(error, AITeddyError) or error.http_status >= 500 else "warning"

        log_data = {
            "error_type": type(error).__name__,
            "error_message": str(error),
            "context": context or {},
            "user_id": user_id,
            "child_id": f"child_{hash(child_id)}" if child_id else None, # Anonymize child ID
            "traceback": traceback.format_exc() if log_level == "error" else None
        }

        if isinstance(error, AITeddyError):
            log_data["error_code"] = error.error_code
            log_data["details"] = error.details

        getattr(logger, log_level)(f"Error handled: {type(error).__name__}", extra=log_data)

def get_error_response(
    error: Union[AITeddyError, Exception],
    include_details: bool = False
) -> Dict[str, Any]:
    """
    Generate a standardized error response dictionary.

    Args:
        error: The exception object.
        include_details: Whether to include detailed error information.

    Returns:
        A dictionary representing the standardized error response.
    """
    handler = ErrorHandler(log_errors=False, include_details=include_details)
    return handler.handle_error(error)
"""