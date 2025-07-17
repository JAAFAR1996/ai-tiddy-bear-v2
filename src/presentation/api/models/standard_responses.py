"""from datetime import datetime
from enum import Enum
from typing import Any, Dict, List, Optional, Union
from pydantic import BaseModel, Field.
"""

"""🔄 Standardized API Response Models
Consistent naming conventions for all API responses"""


class ResponseStatus(str, Enum):
    """Standardized response status values."""

    SUCCESS = "success"
    ERROR = "error"
    WARNING = "warning"
    PARTIAL = "partial"


class ResponseCode(str, Enum):
    """Standardized response codes for consistent API communication."""

    OK = "ok"
    CREATED = "created"
    ACCEPTED = "accepted"
    NO_CONTENT = "no_content"
    BAD_REQUEST = "bad_request"
    UNAUTHORIZED = "unauthorized"
    FORBIDDEN = "forbidden"
    NOT_FOUND = "not_found"
    CONFLICT = "conflict"
    UNPROCESSABLE_ENTITY = "unprocessable_entity"
    INTERNAL_ERROR = "internal_error"
    SERVICE_UNAVAILABLE = "service_unavailable"


class StandardAPIResponse(BaseModel):
    """Standardized API response format for consistent client communication.
    All API endpoints should use this format or inherit from it.
    """

    status: ResponseStatus = Field(description="Response status indicator")
    message: Optional[str] = Field(default=None, description="Human-readable message")
    data: Optional[Union[Dict[str, Any], List[Any], str, int, float, bool]] = Field(
        default=None,
        description="Response payload data",
    )
    errors: Optional[List[Dict[str, Any]]] = Field(
        default=None,
        description="Error details if applicable",
    )
    metadata: Optional[Dict[str, Any]] = Field(
        default=None,
        description="Additional response metadata",
    )
    timestamp: datetime = Field(
        default_factory=datetime.now,
        description="Response generation timestamp",
    )
    request_id: Optional[str] = Field(
        default=None,
        description="Request tracking ID for debugging",
    )

    class Config:
        """Pydantic configuration."""

        use_enum_values = True
        json_encoders = {datetime: lambda v: v.isoformat()}


class SuccessResponse(StandardAPIResponse):
    """Success response with data payload."""

    status: ResponseStatus = ResponseStatus.SUCCESS
    message: str = "Operation completed successfully"


class ErrorResponse(StandardAPIResponse):
    """Error response with error details."""

    status: ResponseStatus = ResponseStatus.ERROR
    data: None = None


class ChildSafetyResponse(StandardAPIResponse):
    """Specialized response for child safety operations.
    Includes COPPA compliance indicators and safety metadata.
    """

    safety_validated: bool = Field(description="Content passed safety validation")
    coppa_compliant: bool = Field(description="Response is COPPA compliant")
    age_appropriate: bool = Field(description="Content is age-appropriate")
    content_rating: Optional[str] = Field(
        default=None,
        description="Content safety rating",
    )


class AuthenticationResponse(StandardAPIResponse):
    """Authentication response with tokens and user info."""

    access_token: str = Field(description="JWT access token")
    refresh_token: str = Field(description="JWT refresh token")
    token_type: str = Field(default="bearer", description="Token type")
    expires_in: int = Field(description="Token expiration time in seconds")
    user_info: Dict[str, Any] = Field(description="Authenticated user information")
    permissions: List[str] = Field(default_factory=list, description="User permissions")


class PaginatedResponse(StandardAPIResponse):
    """Paginated response with metadata."""

    total_count: int = Field(description="Total number of items")
    page_number: int = Field(description="Current page number (1-based)")
    page_size: int = Field(description="Number of items per page")
    total_pages: int = Field(description="Total number of pages")
    has_next: bool = Field(description="Whether there is a next page")
    has_previous: bool = Field(description="Whether there is a previous page")


class HealthCheckResponse(StandardAPIResponse):
    """Health check response with system status."""

    service_status: str = Field(description="Overall service health status")
    dependencies: Dict[str, Dict[str, Any]] = Field(
        description="Status of external dependencies",
    )
    uptime_seconds: float = Field(description="Service uptime in seconds")
    version: str = Field(description="Application version")
    environment: str = Field(description="Deployment environment")


class ValidationErrorDetail(BaseModel):
    """Detailed validation error information."""

    field: str = Field(description="Field name that failed validation")
    message: str = Field(description="Validation error message")
    code: str = Field(description="Error code for programmatic handling")
    invalid_value: Optional[Any] = Field(
        default=None,
        description="The invalid value that caused the error",
    )


class ValidationErrorResponse(ErrorResponse):
    """Validation error response with field - specific details."""

    validation_errors: List[ValidationErrorDetail] = Field(
        description="Detailed validation error information",
    )


def create_success_response(
    data: Any = None,
    message: str = "Operation completed successfully",
    metadata: Optional[Dict[str, Any]] = None,
    request_id: Optional[str] = None,
) -> StandardAPIResponse:
    """Create a standardized success response.
    Args: data: Response data payload
        message: Success message
        metadata: Additional metadata
        request_id: Request tracking ID
    Returns: Standardized success response.
    """
    return StandardAPIResponse(
        status=ResponseStatus.SUCCESS,
        message=message,
        data=data,
        metadata=metadata,
        request_id=request_id,
    )


def create_error_response(
    message: str,
    errors: Optional[List[Dict[str, Any]]] = None,
    metadata: Optional[Dict[str, Any]] = None,
    request_id: Optional[str] = None,
) -> StandardAPIResponse:
    """Create a standardized error response.
    Args: message: Error message
        errors: Detailed error information
        metadata: Additional metadata
        request_id: Request tracking ID
    Returns: Standardized error response.
    """
    return StandardAPIResponse(
        status=ResponseStatus.ERROR,
        message=message,
        data=None,
        errors=errors,
        metadata=metadata,
        request_id=request_id,
    )


def create_child_safety_response(
    data: Any,
    safety_validated: bool,
    coppa_compliant: bool,
    age_appropriate: bool,
    content_rating: Optional[str] = None,
    message: str = "Child safety validated",
    request_id: Optional[str] = None,
) -> ChildSafetyResponse:
    """Create a child safety compliant response.
    Args: data: Response data
        safety_validated: Whether content passed safety checks
        coppa_compliant: Whether response is COPPA compliant
        age_appropriate: Whether content is age - appropriate
        content_rating: Content safety rating
        message: Response message
        request_id: Request tracking ID
    Returns: Child safety response.
    """
    return ChildSafetyResponse(
        status=ResponseStatus.SUCCESS,
        message=message,
        data=data,
        safety_validated=safety_validated,
        coppa_compliant=coppa_compliant,
        age_appropriate=age_appropriate,
        content_rating=content_rating,
        request_id=request_id,
    )


def create_paginated_response(
    data: List[Any],
    total_count: int,
    page_number: int,
    page_size: int,
    message: str = "Data retrieved successfully",
    metadata: Optional[Dict[str, Any]] = None,
    request_id: Optional[str] = None,
) -> PaginatedResponse:
    """Create a paginated response.
    Args: data: List of items for current page
        total_count: Total number of items
        page_number: Current page number(1 - based)
        page_size: Number of items per page
        message: Response message
        metadata: Additional metadata
        request_id: Request tracking ID
    Returns: Paginated response.
    """
    total_pages = (total_count + page_size - 1) // page_size
    return PaginatedResponse(
        status=ResponseStatus.SUCCESS,
        message=message,
        data=data,
        metadata=metadata,
        total_count=total_count,
        page_number=page_number,
        page_size=page_size,
        total_pages=total_pages,
        has_next=page_number < total_pages,
        has_previous=page_number > 1,
        request_id=request_id,
    )


NAMING_CONVENTIONS = {
    "field_names": {
        "use_snake_case": True,
        "avoid_abbreviations": True,
        "be_descriptive": True,
    },
    "response_keys": {
        "status": "status",  # Always use 'status' not 'result' or 'success'
        "message": "message",  # Always use 'message' not 'msg' or 'description'
        "data": "data",  # Always use 'data' not 'payload' or 'response'
        "errors": "errors",  # Always use 'errors' not 'error' for arrays
        "metadata": "metadata",  # Always use 'metadata' not 'meta' or 'info'
        "timestamp": "timestamp",  # Always use 'timestamp' not 'time' or 'date'
    },
    "boolean_fields": {
        "use_positive_names": True,  # is_active not is_inactive
        "prefix_with_is_has_can": True,  # is_valid, has_permission, can_access
    },
    "id_fields": {
        "suffix_with_id": True,  # user_id not user_identifier
        "use_uuid_format": True,  # When possible use UUID format
    },
}


__all__ = [
    "NAMING_CONVENTIONS",
    "AuthenticationResponse",
    "ChildSafetyResponse",
    "ErrorResponse",
    "HealthCheckResponse",
    "PaginatedResponse",
    "ResponseCode",
    "ResponseStatus",
    "StandardAPIResponse",
    "SuccessResponse",
    "ValidationErrorDetail",
    "ValidationErrorResponse",
    "create_child_safety_response",
    "create_error_response",
    "create_paginated_response",
    "create_success_response",
]
