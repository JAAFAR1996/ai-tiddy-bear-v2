"""Pydantic Models for API Input Validation
Provides comprehensive input validation for all API endpoints
with COPPA compliance and child safety features.
"""

import base64
import os.path
import re
from datetime import date, datetime
from enum import Enum
from typing import Any
from uuid import UUID

from pydantic import BaseModel, EmailStr, Field, validator, field_validator


class ChildAgeGroup(str, Enum):
    """Valid age groups for children."""

    PRESCHOOL = "preschool"  # 3-5
    ELEMENTARY = "elementary"  # 6-8
    MIDDLE_ELEMENTARY = "middle_elementary"  # 9-11
    MIDDLE_SCHOOL = "middle_school"  # 12-13


class LanguageCode(str, Enum):
    """Supported language codes."""

    ENGLISH = "en"
    ARABIC = "ar"
    SPANISH = "es"
    FRENCH = "fr"


class ContentSafetyLevel(str, Enum):
    """Content safety levels for filtering."""

    STRICT = "strict"  # Maximum filtering for young children
    MODERATE = "moderate"  # Balanced filtering
    RELAXED = "relaxed"  # Minimal filtering for older children


class MessageRequest(BaseModel):
    """Request model for child message validation."""

    message: str = Field(
        ...,
        min_length=1,
        max_length=1000,
        description="Child's message",
    )
    child_id: UUID = Field(..., description="Unique identifier for the child")
    language: LanguageCode = Field(
        default=LanguageCode.ENGLISH,
        description="Message language",
    )
    safety_level: ContentSafetyLevel = Field(
        default=ContentSafetyLevel.STRICT, description="Content safety filtering level"
    )

    @classmethod
    @field_validator("message")
    @classmethod
    def validate_message_content(cls, v) -> str:
        """Validate message content for child safety."""
        if not v or not v.strip():
            raise ValueError("Message cannot be empty")

        # Basic safety checks - prohibited keywords that could indicate unsafe content
        prohibited_keywords = [
            "password",
            "secret",
            "address",
            "phone",
            "email",
            "meet",
            "location",
            "visit",
            "come over",
            "real name",
            "where do you live",
            "personal information",
            "credit card",
            "social security",
        ]

        message_lower = v.lower()
        for keyword in prohibited_keywords:
            if keyword in message_lower:
                raise ValueError(f"Message contains prohibited content: {keyword}")

        # Check for excessive repetition (spam protection)
        words = v.split()
        if len(words) > 10:
            unique_words = set(word.lower() for word in words)
            if len(unique_words) / len(words) < 0.3:  # Less than 30% unique words
                raise ValueError("Message appears to be spam or excessive repetition")

        return v.strip()


class ChildRegistrationRequest(BaseModel):
    """Request model for child registration with COPPA compliance."""

    name: str = Field(..., min_length=1, max_length=100, description="Child's name")
    age: int = Field(
        ...,
        ge=3,
        le=13,
        description="Child's age (3-13 for COPPA compliance)",
    )
    parent_email: EmailStr = Field(..., description="Parent's email for consent")
    language_preference: LanguageCode = Field(default=LanguageCode.ENGLISH)
    date_of_birth: date | None = Field(None, description="Optional birth date")
    personality_traits: list[str] = Field(default_factory=list, max_items=10)
    allowed_topics: list[str] = Field(default_factory=list, max_items=20)
    restricted_topics: list[str] = Field(default_factory=list, max_items=20)
    emergency_contact_name: str | None = Field(
        None, max_length=100, description="Emergency contact name"
    )
    emergency_contact_phone: str | None = Field(
        None, max_length=20, description="Emergency contact phone"
    )

    @classmethod
    @field_validator("name")
    @classmethod
    def validate_name(cls, v) -> str:
        """Validate child name."""
        if not v or not v.strip():
            raise ValueError("Name is required")

        # Remove excessive whitespace
        name = " ".join(v.strip().split())

        # Basic safety check - no numbers or special characters except common ones
        allowed_chars = set("abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ -'")
        if not all(char in allowed_chars for char in name):
            raise ValueError(
                "Name should only contain letters, spaces, hyphens, and apostrophes"
            )

        # Prevent extremely long names
        if len(name) > 50:
            raise ValueError("Name is too long")

        return name
    @classmethod

    @field_validator("age")
    @classmethod
    def validate_coppa_age(cls, v) -> int:
        """Validate age for COPPA compliance."""
        if v < 3:
            raise ValueError("Children under 3 years are not supported")
        if v > 13:
            raise ValueError(
                "COPPA compliance: Children over 13 require different consent procedures"
            )
        return v
    @field_validator("date_of_birth")
    @classmethod
    def validate_birth_date(cls, v, values) -> date | None:
        """Validate birth date consistency with age."""
        if v and "age" in values:
            today = date.today()
            calculated_age = (
                today.year - v.year - ((today.month, today.day) < (v.month, v.day))
            )
            if abs(calculated_age - values["age"]) > 1:
                raise ValueError("Birth date does not match provided age")

    @field_validator("personality_traits")
    @classmethod
    def validate_personality_traits(cls, v) -> list[str]:
        """Validate personality traits."""
        if not v:
            return v

        # Ensure traits are appropriate and not too long
        valid_traits = []
        for trait in v:
            if not isinstance(trait, str):
                continue
            trait = trait.strip()
            if len(trait) > 50:
                raise ValueError("Personality trait too long")
            if trait:
                valid_traits.append(trait)

        return valid_traits[:10]  # Limit to 10 traits


class AudioMessageRequest(BaseModel):
    """Request model for audio message processing."""

    audio_data: str = Field(..., description="Base64 encoded audio data")
    child_id: UUID = Field(..., description="Child identifier")
    language_code: LanguageCode = Field(default=LanguageCode.ENGLISH)
    duration_seconds: float | None = Field(
        None,
        ge=0.1,
        le=60.0,
        description="Audio duration in seconds",
    )
    audio_format: str = Field(default="wav", description="Audio format (wav, mp3, ogg)")

    @field_validator("audio_data")
    @classmethod
    def validate_audio_data(cls, v) -> str:
        """Validate base64 audio data."""
        if not v:
            raise ValueError("Audio data is required")

        # Basic base64 validation
        try:
            decoded = base64.b64decode(v)
            if len(decoded) == 0:
                raise ValueError("Audio data is empty")
            if len(decoded) > 10 * 1024 * 1024:  # 10MB limit
                raise ValueError("Audio data too large (max 10MB)")
            if len(decoded) < 100:  # Minimum size check
                raise ValueError("Audio data too small to be valid")
        except Exception as e:
            raise ValueError(f"Invalid base64 audio data: {e!s}")

        return v

    @field_validator("audio_format")
    @classmethod
    def validate_audio_format(cls, v) -> str:
        """Validate audio format."""
        allowed_formats = ["wav", "mp3", "ogg", "m4a", "webm"]
        if v.lower() not in allowed_formats:
            raise ValueError(f"Audio format must be one of: {allowed_formats}")
        return v.lower()


class EmergencyContactRequest(BaseModel):
    """Request model for emergency contact information."""

    name: str = Field(..., min_length=1, max_length=100)
    relationship: str = Field(..., min_length=1, max_length=50)
    phone: str = Field(..., min_length=10, max_length=20)
    email: EmailStr | None = None
    is_primary: bool = Field(default=False)
    can_authorize_emergency: bool = Field(default=True)

    @field_validator("phone")
    @classmethod
    def validate_phone(cls, v) -> str:
        """Validate phone number format."""
        # Remove all non-digits
        digits_only = re.sub(r"\D", "", v)
        if len(digits_only) < 10:
            raise ValueError("Phone number must have at least 10 digits")
        if len(digits_only) > 15:
            raise ValueError("Phone number too long")
        return digits_only

    @field_validator("relationship")
    @classmethod
    def validate_relationship(cls, v) -> str:
        """Validate relationship type."""
        valid_relationships = [
            "parent",
            "guardian",
            "grandparent",
            "aunt",
            "uncle",
            "sibling",
            "family_friend",
            "babysitter",
            "teacher",
        ]
        if v.lower() not in valid_relationships:
            raise ValueError(f"Relationship must be one of: {valid_relationships}")
        return v.lower()


class ParentConsentRequest(BaseModel):
    """Request model for parental consent verification."""

    parent_email: EmailStr = Field(..., description="Parent's email")
    child_id: UUID = Field(..., description="Child requiring consent")
    consent_type: str = Field(..., description="Type of consent requested")
    verification_method: str = Field(..., description="Method for verification")
    additional_info: dict[str, Any] | None = Field(default_factory=dict)
    consent_duration_days: int = Field(
        default=90, ge=1, le=365, description="Consent validity period"
    )

    @field_validator("consent_type")
    @classmethod
    def validate_consent_type(cls, v) -> str:
        """Validate consent type."""
        valid_types = [
            "data_collection",
            "voice_recording",
            "ai_interaction",
            "content_sharing",
            "emergency_contact",
            "location_services",
            "third_party_integration",
            "personalization",
            "analytics",
        ]
        if v not in valid_types:
            raise ValueError(f"Invalid consent type. Must be one of: {valid_types}")
        return v

    @field_validator("verification_method")
    @classmethod
    def validate_verification_method(cls, v) -> str:
        """Validate verification method."""
        valid_methods = [
            "email_verification",
            "sms_verification",
            "phone_call_verification",
            "credit_card_verification",
            "government_id_verification",
            "digital_signature",
        ]
        if v not in valid_methods:
            raise ValueError(
                f"Invalid verification method. Must be one of: {valid_methods}"
            )
        return v


class HealthCheckRequest(BaseModel):
    """Request model for health check endpoints."""

    detailed: bool = Field(
        default=False,
        description="Include detailed health information",
    )
    include_metrics: bool = Field(
        default=False,
        description="Include performance metrics",
    )
    check_dependencies: bool = Field(
        default=True, description="Check external dependencies"
    )


class PaginationRequest(BaseModel):
    """Request model for paginated endpoints."""

    page: int = Field(default=1, ge=1, description="Page number (1-based)")
    limit: int = Field(default=20, ge=1, le=100, description="Items per page")
    sort_by: str | None = Field(None, max_length=50, description="Sort field")
    sort_order: str | None = Field(
        "asc",
        pattern="^(asc|desc)$",
        description="Sort order",
    )

    @field_validator("limit")
    @classmethod
    def validate_child_safe_limit(cls, v) -> int:
        """Ensure pagination limits are child-safe."""
        # For child data, limit to smaller pages for safety and performance
        if v > 50:
            raise ValueError("Page limit too high for child data (max 50)")
        return v

    @field_validator("sort_by")
    @classmethod
    def validate_sort_field(cls, v) -> str | None:
        """Validate sort field for security."""
        if v is None:
            return v

        # Prevent SQL injection and ensure only safe field names
        allowed_sort_fields = [
            "name",
            "age",
            "created_at",
            "updated_at",
            "language",
            "safety_score",
            "last_activity",
        ]
        if v not in allowed_sort_fields:
            raise ValueError(f"Sort field must be one of: {allowed_sort_fields}")
        return v


class FileUploadRequest(BaseModel):
    """Request model for file uploads with safety validation."""

    filename: str = Field(..., min_length=1, max_length=255)
    content_type: str = Field(..., description="MIME type of the file")
    file_size: int = Field(
        ...,
        ge=1,
        le=50 * 1024 * 1024,  # 50MB limit
        description="File size in bytes",
    )
    child_id: UUID | None = Field(None, description="Associated child ID if applicable")

    @field_validator("filename")
    @classmethod
    def validate_filename_safety(cls, v) -> str:
        """Validate filename for path traversal and safety."""
        # Remove any path separators
        filename = os.path.basename(v)

        # Check for dangerous patterns
        dangerous_patterns = [
            "..",
            "/",
            "\\",
            ":",
            "*",
            "?",
            '"',
            "<",
            ">",
            "|",
            "con",
            "prn",
            "aux",
            "nul",  # Windows reserved names
        ]

        filename_lower = filename.lower()
        for pattern in dangerous_patterns:
            if pattern in filename_lower:
                raise ValueError(f"Filename contains dangerous pattern: {pattern}")

        # Ensure reasonable length and valid extension
        if len(filename) > 100:
            raise ValueError("Filename too long")

        return filename

    @field_validator("content_type")
    @classmethod
    def validate_content_type(cls, v) -> str:
        """Validate allowed content types."""
        allowed_types = [
            "image/jpeg",
            "image/png",
            "image/gif",
            "image/webp",
            "audio/wav",
            "audio/mp3",
            "audio/ogg",
            "audio/webm",
            "text/plain",
            "application/json",
        ]
        if v not in allowed_types:
            raise ValueError(f"Content type not allowed: {v}")
        return v


class ConversationRequest(BaseModel):
    """Request model for conversation interactions."""

    child_id: UUID = Field(..., description="Child identifier")
    message: str = Field(..., min_length=1, max_length=2000)
    conversation_id: UUID | None = Field(None, description="Existing conversation ID")
    context: dict[str, Any] | None = Field(default_factory=dict)
    safety_level: ContentSafetyLevel = Field(default=ContentSafetyLevel.STRICT)

    @field_validator("message")
    @classmethod
    def validate_conversation_message(cls, v) -> str:
        """Validate conversation message content."""
        if not v or not v.strip():
            raise ValueError("Message cannot be empty")

        # Remove excessive whitespace
        cleaned_message = " ".join(v.strip().split())

        # Check for reasonable length
        if len(cleaned_message.split()) > 300:  # ~300 words max
            raise ValueError("Message too long")

        return cleaned_message


# Response models for consistent API responses
class APIResponse(BaseModel):
    """Standard API response wrapper."""

    success: bool = Field(..., description="Request success status")
    message: str = Field(..., description="Response message")
    data: Any | None = Field(None, description="Response data")
    errors: list[str] | None = Field(None, description="Error details")
    timestamp: datetime = Field(default_factory=datetime.utcnow)
    request_id: str | None = Field(None, description="Request tracking ID")



class LoginRequest(BaseModel):
    """Login request model."""
    email: EmailStr
    password: str


class LoginResponse(BaseModel):
    """Login response model."""
    access_token: str
    refresh_token: str
    token_type: str = "bearer"
    user_id: str
    email: str
    role: str
