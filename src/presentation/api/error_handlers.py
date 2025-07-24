"""Minimal Error Handlers for API Endpoints - TEMPORARY IMPLEMENTATION"""

from fastapi import HTTPException

from src.infrastructure.logging_config import get_logger

logger = get_logger(__name__, component="api")


class AITeddyErrorHandler:
    """Temporary error handler class to fix import cascade issues."""

    @staticmethod
    def handle_authentication_error(
        error=None, operation="", user_message="Authentication required"
    ):
        """Handle authentication errors."""
        logger.warning(f"Authentication error in {operation}: {error}")
        return HTTPException(status_code=401, detail=user_message)

    @staticmethod
    def handle_authorization_error(operation="", user_message="Access denied"):
        """Handle authorization errors."""
        logger.warning(f"Authorization error in {operation}")
        return HTTPException(status_code=403, detail=user_message)

    @staticmethod
    def handle_validation_error(error, operation="", user_message="Invalid input"):
        """Handle validation errors."""
        logger.warning(f"Validation error in {operation}: {error}")
        return HTTPException(status_code=400, detail=user_message)

    @staticmethod
    def handle_not_found_error(resource, resource_id, operation=""):
        """Handle not found errors."""
        logger.warning(f"Resource not found in {operation}: {resource} {resource_id}")
        return HTTPException(status_code=404, detail=f"{resource} not found")

    @staticmethod
    def handle_internal_error(
        error, operation="", user_message="Internal server error"
    ):
        """Handle internal errors."""
        logger.error(f"Internal error in {operation}: {error}")
        return HTTPException(status_code=500, detail=user_message)


def validate_child_access(user_context, child_id):
    """Child access validation with basic permission checks."""
    if not user_context:
        raise HTTPException(status_code=401, detail="Authentication required")

    user_id = user_context.get("user_id")
    if not user_id:
        raise HTTPException(status_code=401, detail="Invalid user context")

    child_ids = user_context.get("child_ids", [])

    if child_id not in child_ids:
        raise HTTPException(status_code=403, detail="Access denied to child data")

    return True
