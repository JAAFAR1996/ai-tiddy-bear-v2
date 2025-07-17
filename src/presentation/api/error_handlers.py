"""
from typing import Any, Dict, Optional
from uuid import uuid4
import logging
from fastapi import HTTPException, status
import traceback
"""

Centralized Error Handling for Child Safety API
Consistent, secure error handling across all endpoints
"""

from src.infrastructure.logging_config import get_logger
logger = get_logger(__name__, component="api")

class SecurityError(Exception):
    """Custom exception for security - related errors"""
    pass

class ChildSafetyError(Exception):
    """Custom exception for child safety violations"""
    pass

class APIErrorHandler:
    """
    Centralized error handler providing consistent, secure error responses
    across all API endpoints while protecting sensitive information.
    """
    @staticmethod
    def handle_validation_error(
        error: Exception,
        operation: str,
        user_message: str = "Invalid input provided"
    ) -> HTTPException:
        """Handle input validation errors(400)"""
        error_id = str(uuid4())[:8]
        logger.warning(f"Validation error [{error_id}] in {operation}: {error}")
        return HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail={
                "error": "validation_error",
                "message": user_message,
                "error_id": error_id
            }
        )

    @staticmethod
    def handle_authentication_error(
        error: Optional[Exception] = None,
        operation: str = "authentication",
        user_message: str = "Authentication required"
    ) -> HTTPException:
        """Handle authentication errors(401)"""
        error_id = str(uuid4())[:8]
        if error:
            logger.warning(f"Authentication error [{error_id}] in {operation}: {error}")
        return HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail={
                "error": "authentication_required",
                "message": user_message,
                "error_id": error_id
            },
            headers={"WWW-Authenticate": "Bearer"}
        )

    @staticmethod
    def handle_authorization_error(
        error: Optional[Exception] = None,
        operation: str = "authorization",
        user_message: str = "Access denied"
    ) -> HTTPException:
        """Handle authorization errors(403)"""
        error_id = str(uuid4())[:8]
        if error:
            logger.warning(f"Authorization error [{error_id}] in {operation}: {error}")
        return HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail={
                "error": "access_denied",
                "message": user_message,
                "error_id": error_id
            }
        )

    @staticmethod
    def handle_not_found_error(
        resource: str,
        resource_id: Optional[str] = None,
        operation: str = "resource_lookup"
    ) -> HTTPException:
        """Handle resource not found errors(404)"""
        error_id = str(uuid4())[:8]
        if resource_id:
            logger.info(f"Resource not found [{error_id}] in {operation}: {resource} with ID {resource_id}")
            user_message = f"{resource.title()} not found"
        else:
            logger.info(f"Resource not found [{error_id}] in {operation}: {resource}")
            user_message = f"{resource.title()} not found"
        return HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail={
                "error": "resource_not_found",
                "message": user_message,
                "error_id": error_id
            }
        )

    @staticmethod
    def handle_child_safety_error(
        error: ChildSafetyError,
        operation: str,
        user_message: str = "Content does not meet safety standards"
    ) -> HTTPException:
        """Handle child safety violations(422)"""
        error_id = str(uuid4())[:8]
        logger.critical(f"CHILD SAFETY VIOLATION [{error_id}] in {operation}: {error}")
        return HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail={
                "error": "safety_violation",
                "message": user_message,
                "error_id": error_id
            }
        )

    @staticmethod
    def handle_rate_limit_error(
        operation: str,
        retry_after: Optional[int] = None
    ) -> HTTPException:
        """Handle rate limiting errors(429)"""
        error_id = str(uuid4())[:8]
        logger.warning(f"Rate limit exceeded [{error_id}] in {operation}")
        headers = {}
        if retry_after:
            headers["Retry-After"] = str(retry_after)
        return HTTPException(
            status_code=status.HTTP_429_TOO_MANY_REQUESTS,
            detail={
                "error": "rate_limit_exceeded",
                "message": "Too many requests. Please try again later.",
                "error_id": error_id
            },
            headers=headers
        )

    @staticmethod
    def handle_internal_error(
        error: Exception,
        operation: str,
        user_message: str = "An internal error occurred"
    ) -> HTTPException:
        """Handle internal server errors(500)"""
        error_id = str(uuid4())[:8]
        logger.error(
            f"Internal error [{error_id}] in {operation}: {error}\n"
            f"Traceback: {traceback.format_exc()}"
        )
        return HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail={
                "error": "internal_error",
                "message": user_message,
                "error_id": error_id
            }
        )

    @staticmethod
    def handle_service_unavailable_error(
        service: str,
        operation: str,
        error: Optional[Exception] = None
    ) -> HTTPException:
        """Handle service unavailability errors(503)"""
        error_id = str(uuid4())[:8]
        if error:
            logger.error(f"Service unavailable [{error_id}] in {operation}: {service} - {error}")
        else:
            logger.error(f"Service unavailable [{error_id}] in {operation}: {service}")
        return HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail={
                "error": "service_unavailable",
                "message": f"{service} is temporarily unavailable",
                "error_id": error_id
            }
        )

    @staticmethod
    def handle_generic_error(
        error: Exception,
        operation: str,
        default_status: int = status.HTTP_500_INTERNAL_SERVER_ERROR,
        user_message: Optional[str] = None
    ) -> HTTPException:
        """
        Generic error handler that routes to appropriate specific handlers
        based on error type and context.
        """
        if isinstance(error, HTTPException):
            # Re-raise existing HTTP exceptions
            raise error
        
        if isinstance(error, ChildSafetyError):
            return APIErrorHandler.handle_child_safety_error(error, operation)
        
        if isinstance(error, SecurityError):
            return APIErrorHandler.handle_authorization_error(error, operation)
        
        if isinstance(error, (ValueError, TypeError)):
            return APIErrorHandler.handle_validation_error(
                error, operation, user_message or "Invalid input provided"
            )
        
        # Default to internal error
        return APIErrorHandler.handle_internal_error(
            error, operation, user_message or "An unexpected error occurred"
        )

def safe_execute(operation: str, user_message: str = None):
    """
    Decorator for safe execution with consistent error handling.
    Usage: @ safe_execute("user_registration") async def register_user(data):
            # Your code here
    """
    def decorator(func):
        async def wrapper(*args, **kwargs):
            try:
                return await func(*args, **kwargs)
            except Exception as e:
                raise APIErrorHandler.handle_generic_error(
                    e, operation, user_message=user_message
                )
        return wrapper
    return decorator

def validate_child_access(current_user: Dict[str, Any], child_id: str) -> None:
    """
    Validate that the current user has access to the specified child.
    Raises appropriate exceptions for COPPA compliance.
    """
    user_child_ids = current_user.get("child_ids", [])
    if child_id not in user_child_ids and current_user.get("role") != "admin":
        raise APIErrorHandler.handle_authorization_error(
            operation="child_access_validation",
            user_message="You do not have permission to access this child's data"
        )

__all__ = [
    "APIErrorHandler",
    "SecurityError",
    "ChildSafetyError",
    "safe_execute",
    "validate_child_access"
]