"""🔄 Standardized API Response Models
Consistent naming conventions for all API responses
"""

from datetime import datetime
from enum import Enum
from typing import Any

from pydantic import BaseModel, Field


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
    message: str | None = Field(default=None, description="Human-readable message")
    data: dict[str, Any] | list[Any] | str | int | float | bool | None = Field(
        default=None,
        description="Response payload data",
    )
    errors: list[dict[str, Any]] | None = Field(
        default=None,
        description="Error details if applicable",
    )
    metadata: dict[str, Any] | None = Field(
        default=None,
        description="Additional response metadata",
    )
    timestamp: datetime = Field(
        default_factory=datetime.now,
        description="Response generation timestamp",
    )
    request_id: str | None = Field(
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
    content_rating: str | None = Field(
        default=None,
        description="Content safety rating",
    )
    parental_controls_active: bool = Field(
        default=True, description="Whether parental controls are active"
    )
    ai_safety_mode: str = Field(
        default="child-mode", description="AI safety mode for content generation"
    )


class TeddyBearResponse(ChildSafetyResponse):
    """Specialized response for AI Teddy Bear interactions."""

    voice_processing_safe: bool = Field(
        default=True, description="Voice processing completed safely"
    )
    emergency_contact_available: bool = Field(
        default=True, description="Emergency contact system is available"
    )
    session_time_remaining: int | None = Field(
        default=None, description="Remaining session time in seconds"
    )
    parental_notification_sent: bool = Field(
        default=False, description="Whether parents were notified of this interaction"
    )


class AuthenticationResponse(StandardAPIResponse):
    """Authentication response with tokens and user info."""

    access_token: str = Field(description="JWT access token")
    refresh_token: str = Field(description="JWT refresh token")
    token_type: str = Field(default="bearer", description="Token type")
    expires_in: int = Field(description="Token expiration time in seconds")
    user_info: dict[str, Any] = Field(description="Authenticated user information")
    permissions: list[str] = Field(default_factory=list, description="User permissions")


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
    dependencies: dict[str, dict[str, Any]] = Field(
        description="Status of external dependencies",
    )
    uptime_seconds: float = Field(description="Service uptime in seconds")
    version: str = Field(description="Application version")
    environment: str = Field(description="Deployment environment")
    child_safety_systems: dict[str, str] = Field(
        default_factory=lambda: {
            "content_filter": "active",
            "coppa_compliance": "enabled",
            "parental_controls": "available",
            "emergency_contact": "ready",
        },
        description="Child safety systems status",
    )


class ValidationErrorDetail(BaseModel):
    """Detailed validation error information."""

    field: str = Field(description="Field name that failed validation")
    message: str = Field(description="Validation error message")
    code: str = Field(description="Error code for programmatic handling")
    invalid_value: Any | None = Field(
        default=None,
        description="The invalid value that caused the error",
    )


class ValidationErrorResponse(ErrorResponse):
    """Validation error response with field-specific details."""

    validation_errors: list[ValidationErrorDetail] = Field(
        description="Detailed validation error information",
    )


class VoiceProcessingResponse(TeddyBearResponse):
    """Response for voice processing operations."""

    audio_quality_score: float | None = Field(
        default=None, description="Audio quality score (0.0 to 1.0)"
    )
    speech_detected: bool = Field(description="Whether speech was detected in audio")
    language_detected: str | None = Field(
        default=None, description="Detected language code"
    )
    content_moderated: bool = Field(
        default=True, description="Whether content was moderated for safety"
    )


class ConversationResponse(TeddyBearResponse):
    """Response for conversation interactions."""

    conversation_id: str = Field(description="Unique conversation identifier")
    turn_number: int = Field(description="Turn number in conversation")
    ai_response_generated: bool = Field(
        description="Whether AI response was successfully generated"
    )
    response_safety_score: float = Field(
        description="Safety score of AI response (0.0 to 1.0)"
    )


def create_success_response(
    data: Any = None,
    message: str = "Operation completed successfully",
    metadata: dict[str, Any] | None = None,
    request_id: str | None = None,
) -> StandardAPIResponse:
    """Create a standardized success response.

    Args:
        data: Response data payload
        message: Success message
        metadata: Additional metadata
        request_id: Request tracking ID

    Returns:
        Standardized success response
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
    errors: list[dict[str, Any]] | None = None,
    metadata: dict[str, Any] | None = None,
    request_id: str | None = None,
) -> StandardAPIResponse:
    """Create a standardized error response.

    Args:
        message: Error message
        errors: Detailed error information
        metadata: Additional metadata
        request_id: Request tracking ID

    Returns:
        Standardized error response
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
    content_rating: str | None = None,
    message: str = "Child safety validated",
    request_id: str | None = None,
) -> ChildSafetyResponse:
    """Create a child safety compliant response.

    Args:
        data: Response data
        safety_validated: Whether content passed safety checks
        coppa_compliant: Whether response is COPPA compliant
        age_appropriate: Whether content is age-appropriate
        content_rating: Content safety rating
        message: Response message
        request_id: Request tracking ID

    Returns:
        Child safety response
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


def create_teddy_bear_response(
    data: Any,
    safety_validated: bool = True,
    coppa_compliant: bool = True,
    age_appropriate: bool = True,
    voice_processing_safe: bool = True,
    emergency_contact_available: bool = True,
    session_time_remaining: int | None = None,
    message: str = "Teddy Bear interaction completed safely",
    request_id: str | None = None,
) -> TeddyBearResponse:
    """Create a Teddy Bear specific response.

    Args:
        data: Response data
        safety_validated: Whether content passed safety checks
        coppa_compliant: Whether response is COPPA compliant
        age_appropriate: Whether content is age-appropriate
        voice_processing_safe: Whether voice processing was safe
        emergency_contact_available: Whether emergency contact is available
        session_time_remaining: Remaining session time in seconds
        message: Response message
        request_id: Request tracking ID

    Returns:
        Teddy Bear response
    """
    return TeddyBearResponse(
        status=ResponseStatus.SUCCESS,
        message=message,
        data=data,
        safety_validated=safety_validated,
        coppa_compliant=coppa_compliant,
        age_appropriate=age_appropriate,
        voice_processing_safe=voice_processing_safe,
        emergency_contact_available=emergency_contact_available,
        session_time_remaining=session_time_remaining,
        request_id=request_id,
    )


def create_paginated_response(
    data: list[Any],
    total_count: int,
    page_number: int,
    page_size: int,
    message: str = "Data retrieved successfully",
    metadata: dict[str, Any] | None = None,
    request_id: str | None = None,
) -> PaginatedResponse:
    """Create a paginated response.

    Args:
        data: List of items for current page
        total_count: Total number of items
        page_number: Current page number (1-based)
        page_size: Number of items per page
        message: Response message
        metadata: Additional metadata
        request_id: Request tracking ID

    Returns:
        Paginated response
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


def create_voice_processing_response(
    data: Any,
    audio_quality_score: float | None = None,
    speech_detected: bool = True,
    language_detected: str | None = None,
    content_moderated: bool = True,
    message: str = "Voice processing completed successfully",
    request_id: str | None = None,
) -> VoiceProcessingResponse:
    """Create a voice processing response.

    Args:
        data: Response data
        audio_quality_score: Audio quality score (0.0 to 1.0)
        speech_detected: Whether speech was detected
        language_detected: Detected language code
        content_moderated: Whether content was moderated
        message: Response message
        request_id: Request tracking ID

    Returns:
        Voice processing response
    """
    return VoiceProcessingResponse(
        status=ResponseStatus.SUCCESS,
        message=message,
        data=data,
        safety_validated=True,
        coppa_compliant=True,
        age_appropriate=True,
        audio_quality_score=audio_quality_score,
        speech_detected=speech_detected,
        language_detected=language_detected,
        content_moderated=content_moderated,
        request_id=request_id,
    )


def create_conversation_response(
    data: Any,
    conversation_id: str,
    turn_number: int,
    ai_response_generated: bool = True,
    response_safety_score: float = 1.0,
    message: str = "Conversation processed successfully",
    request_id: str | None = None,
) -> ConversationResponse:
    """Create a conversation response.

    Args:
        data: Response data
        conversation_id: Unique conversation identifier
        turn_number: Turn number in conversation
        ai_response_generated: Whether AI response was generated
        response_safety_score: Safety score (0.0 to 1.0)
        message: Response message
        request_id: Request tracking ID

    Returns:
        Conversation response
    """
    return ConversationResponse(
        status=ResponseStatus.SUCCESS,
        message=message,
        data=data,
        safety_validated=True,
        coppa_compliant=True,
        age_appropriate=True,
        conversation_id=conversation_id,
        turn_number=turn_number,
        ai_response_generated=ai_response_generated,
        response_safety_score=response_safety_score,
        request_id=request_id,
    )


# Naming conventions for consistent API design
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
    "child_safety_fields": {
        "safety_validated": "Boolean indicating content safety validation",
        "coppa_compliant": "Boolean indicating COPPA compliance",
        "age_appropriate": "Boolean indicating age appropriateness",
        "content_rating": "String content safety rating",
        "parental_controls_active": "Boolean indicating parental controls status",
        "emergency_contact_available": "Boolean indicating emergency contact availability",
    },
}


# AI Teddy Bear specific response templates
TEDDY_BEAR_RESPONSE_TEMPLATES = {
    "success_interaction": {
        "message": "Great job! I had fun talking with you.",
        "safety_indicators": {
            "safety_validated": True,
            "coppa_compliant": True,
            "age_appropriate": True,
            "voice_processing_safe": True,
        },
    },
    "session_timeout_warning": {
        "message": "We've been playing for a while! Let's take a break soon.",
        "metadata": {
            "warning_type": "session_timeout",
            "recommended_action": "prepare_for_break",
        },
    },
    "emergency_contact": {
        "message": "I'm getting help for you right away.",
        "metadata": {
            "emergency_triggered": True,
            "contact_method": "immediate_notification",
        },
    },
    "inappropriate_content_detected": {
        "message": "Let's talk about something else that's more fun!",
        "safety_indicators": {"content_filtered": True, "alternative_suggested": True},
    },
}


__all__ = [
    "NAMING_CONVENTIONS",
    "TEDDY_BEAR_RESPONSE_TEMPLATES",
    "AuthenticationResponse",
    "ChildSafetyResponse",
    "ConversationResponse",
    "ErrorResponse",
    "HealthCheckResponse",
    "PaginatedResponse",
    "ResponseCode",
    "ResponseStatus",
    "StandardAPIResponse",
    "SuccessResponse",
    "TeddyBearResponse",
    "ValidationErrorDetail",
    "ValidationErrorResponse",
    "VoiceProcessingResponse",
    "create_child_safety_response",
    "create_conversation_response",
    "create_error_response",
    "create_paginated_response",
    "create_success_response",
    "create_teddy_bear_response",
    "create_voice_processing_response",
]
