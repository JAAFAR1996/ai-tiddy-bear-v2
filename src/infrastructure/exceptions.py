"""
Centralized Exception Handling System
"""

from datetime import datetime
from enum import Enum
from typing import Dict, Any, Optional
import logging
from src.infrastructure.logging_config import get_logger

logger = get_logger(__name__, component="infrastructure")

class ErrorCode(Enum):
    """Standardized error codes for API responses"""
    # Authentication errors (1000-1099)
    INVALID_CREDENTIALS = 1001
    TOKEN_EXPIRED = 1002
    INSUFFICIENT_PERMISSIONS = 1003
    ACCOUNT_LOCKED = 1004

    # Child safety errors (2000-2099)
    AGE_RESTRICTION = 2001
    CONTENT_MODERATION_FAILED = 2002
    PARENTAL_CONSENT_REQUIRED = 2003
    INTERACTION_LIMIT_EXCEEDED = 2004
    INAPPROPRIATE_CONTENT = 2005

    # Data validation errors (3000-3099)
    INVALID_INPUT = 3001
    MISSING_REQUIRED_FIELD = 3002
    DATA_TYPE_MISMATCH = 3003
    VALUE_OUT_OF_RANGE = 3004

    # Resource errors (4000-4099)
    RESOURCE_NOT_FOUND = 4001
    RESOURCE_ALREADY_EXISTS = 4002
    RESOURCE_LOCKED = 4003
    RESOURCE_UNAVAILABLE = 4004

    # System errors (5000-5099)
    DATABASE_ERROR = 5001
    EXTERNAL_SERVICE_ERROR = 5002
    CONFIGURATION_ERROR = 5003
    INTERNAL_ERROR = 5000

class BaseApplicationException(Exception):
    """
    Base exception class for all application exceptions.
    """
    def __init__(
        self,
        message: str,
        error_code: ErrorCode,
        details: Optional[Dict[str, Any]] = None,
        user_message: Optional[str] = None,
        child_friendly_message: Optional[str] = None
    ) -> None:
        super().__init__(message)
        self.message = message
        self.error_code = error_code
        self.details = details or {}
        self.user_message = user_message or message
        self.child_friendly_message = child_friendly_message
        self.timestamp = datetime.utcnow()
        # Log the exception
        logger.error(
            f"{self.__class__.__name__}: {message}",
            extra={
                "error_code": error_code.value,
                "details": details
            }
        )

# Specific Exception Classes
class AuthenticationException(BaseApplicationException):
    def __init__(self, message: str = "Authentication failed", error_code: ErrorCode = ErrorCode.INVALID_CREDENTIALS, **kwargs):
        super().__init__(message, error_code, **kwargs)

class ChildSafetyException(BaseApplicationException):
    def __init__(self, message: str = "Child safety violation", error_code: ErrorCode = ErrorCode.INAPPROPRIATE_CONTENT, **kwargs):
        super().__init__(message, error_code, **kwargs)

class DataValidationException(BaseApplicationException):
    def __init__(self, message: str = "Invalid data provided", error_code: ErrorCode = ErrorCode.INVALID_INPUT, **kwargs):
        super().__init__(message, error_code, **kwargs)

class ResourceNotFoundException(BaseApplicationException):
    def __init__(self, resource_name: str, resource_id: Any, **kwargs):
        message = f"{resource_name} with ID '{resource_id}' not found."
        super().__init__(message, ErrorCode.RESOURCE_NOT_FOUND, **kwargs)

class SystemException(BaseApplicationException):
    def __init__(self, message: str = "An internal system error occurred", error_code: ErrorCode = ErrorCode.INTERNAL_ERROR, **kwargs):
        super().__init__(message, error_code, **kwargs)

class ExternalServiceException(BaseApplicationException):
    def __init__(self, service_name: str, original_exception: Optional[Exception] = None, **kwargs):
        message = f"Error communicating with external service: {service_name}"
        details = kwargs.get("details", {})
        if original_exception:
            details["original_exception"] = str(original_exception)
        super().__init__(message, ErrorCode.EXTERNAL_SERVICE_ERROR, details=details, **kwargs)