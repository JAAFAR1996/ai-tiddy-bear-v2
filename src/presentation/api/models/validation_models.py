"""
from datetime import date, datetime
from enum import Enum
from typing import List, Optional, Dict, Any
from uuid import UUID
from pydantic import BaseModel, Field, validator, EmailStr
"""

"""Pydantic Models for API Input Validation
Provides comprehensive input validation for all API endpoints
with COPPA compliance and child safety features."""


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


class MessageRequest(BaseModel):
    """Request model for child message validation."""
    message: str = Field(..., min_length=1, max_length=1000, description="Child's message")
    child_id: UUID = Field(..., description="Unique identifier for the child")
    language: LanguageCode = Field(default=LanguageCode.ENGLISH, description="Message language")

    @validator('message')
    def validate_message_content(cls, v) -> str:
        """Validate message content for child safety."""
        if not v or not v.strip():
            raise ValueError('Message cannot be empty')
        # Basic safety checks
        prohibited_keywords = [
            'password', 'secret', 'address', 'phone', 'email',
            'meet', 'location', 'visit', 'come over'
        ]
        message_lower = v.lower()
        for keyword in prohibited_keywords:
            if keyword in message_lower:
                raise ValueError(f'Message contains prohibited content')
        return v.strip()


class ChildRegistrationRequest(BaseModel):
    """Request model for child registration with COPPA compliance."""
    name: str = Field(..., min_length=1, max_length=100, description="Child's name")
    age: int = Field(..., ge=3, le=13, description="Child's age (3-13 for COPPA compliance)")  # ✅
    parent_email: EmailStr = Field(..., description="Parent's email for consent")
    language_preference: LanguageCode = Field(default=LanguageCode.ENGLISH)
    date_of_birth: Optional[date] = Field(None, description="Optional birth date")
    personality_traits: List[str] = Field(default_factory=list, max_items=10)
    allowed_topics: List[str] = Field(default_factory=list, max_items=20)
    restricted_topics: List[str] = Field(default_factory=list, max_items=20)

    @validator('name')
    def validate_name(cls, v) -> str:
        """Validate child name."""
        if not v or not v.strip():
            raise ValueError('Name is required')
        # Remove excessive whitespace
        name = ' '.join(v.strip().split())
        # Basic safety check - no numbers or special characters
        if not name.replace(' ', '').replace('-', '').replace("'", '').isalpha():
            raise ValueError('Name should only contain letters, spaces, hyphens, and apostrophes')
        return name

    @validator('age')
    def validate_coppa_age(cls, v) -> int:
        """Validate age for COPPA compliance."""
        if v < 3:
            raise ValueError('Children under 3 years are not supported')
        if v > 13:
            raise ValueError('COPPA compliance: Children over 13 require different consent procedures')
        return v

    @validator('date_of_birth')
    def validate_birth_date(cls, v, values) -> datetime:
        """Validate birth date consistency with age."""
        if v and 'age' in values:
            today = date.today()
            calculated_age = today.year - v.year - ((today.month, today.day) < (v.month, v.day))
            if abs(calculated_age - values['age']) > 1:
                raise ValueError('Birth date does not match provided age')
        return v


class AudioMessageRequest(BaseModel):
    """Request model for audio message processing."""
    audio_data: str = Field(..., description="Base64 encoded audio data")
    child_id: UUID = Field(..., description="Child identifier")
    language_code: LanguageCode = Field(default=LanguageCode.ENGLISH)
    duration_seconds: Optional[float] = Field(None, ge=0.1, le=60.0, description="Audio duration")

    @validator('audio_data')
    def validate_audio_data(cls, v) -> bytes:
        """Validate base64 audio data."""
        if not v:
            raise ValueError('Audio data is required')
        # Basic base64 validation
        import base64
        try:
            decoded = base64.b64decode(v)
            if len(decoded) == 0:
                raise ValueError('Audio data is empty')
            if len(decoded) > 10 * 1024 * 1024:  # 10MB limit
                raise ValueError('Audio data too large (max 10MB)')
        except Exception:
            raise ValueError('Invalid base64 audio data')
        return v


class EmergencyContactRequest(BaseModel):
    """Request model for emergency contact information."""
    name: str = Field(..., min_length=1, max_length=100)
    relationship: str = Field(..., min_length=1, max_length=50)
    phone: str = Field(..., min_length=10, max_length=20)
    email: Optional[EmailStr] = None
    is_primary: bool = Field(default=False)

    @validator('phone')
    def validate_phone(cls, v) -> str:
        """Validate phone number format."""
        import re
        # Remove all non-digits
        digits_only = re.sub(r'\\D', '', v)
        if len(digits_only) < 10:
            raise ValueError('Phone number must have at least 10 digits')
        if len(digits_only) > 15:
            raise ValueError('Phone number too long')
        return digits_only


class ParentConsentRequest(BaseModel):
    """Request model for parental consent verification."""
    parent_email: EmailStr = Field(..., description="Parent's email")
    child_id: UUID = Field(..., description="Child requiring consent")
    consent_type: str = Field(..., description="Type of consent requested")
    verification_method: str = Field(..., description="Method for verification")
    additional_info: Optional[Dict[str, Any]] = Field(default_factory=dict)

    @validator('consent_type')
    def validate_consent_type(cls, v) -> str:
        """Validate consent type."""
        valid_types = [
            'data_collection', 'feature_access', 'content_sharing',
            'location_services', 'third_party_integration'
        ]
        if v not in valid_types:
            raise ValueError(f'Invalid consent type. Must be one of: {valid_types}')
        return v

    @validator('verification_method')
    def validate_verification_method(cls, v) -> str:
        """Validate verification method."""
        valid_methods = ['email', 'sms', 'phone_call', 'credit_card', 'government_id']
        if v not in valid_methods:
            raise ValueError(f'Invalid verification method. Must be one of: {valid_methods}')
        return v


class HealthCheckRequest(BaseModel):
    """Request model for health check endpoints."""
    detailed: bool = Field(default=False, description="Include detailed health information")
    include_metrics: bool = Field(default=False, description="Include performance metrics")


class PaginationRequest(BaseModel):
    """Request model for paginated endpoints."""
    page: int = Field(default=1, ge=1, description="Page number (1-based)")
    limit: int = Field(default=20, ge=1, le=100, description="Items per page")
    sort_by: Optional[str] = Field(None, max_length=50, description="Sort field")
    sort_order: Optional[str] = Field("asc", regex="^(asc|desc)$", description="Sort order")

    @validator('limit')
    def validate_child_safe_limit(cls, v) -> int:
        """Ensure pagination limits are child - safe."""
        # For child data, limit to smaller pages for safety
        if v > 50:
            raise ValueError('Page limit too high for child data (max 50)')
        return v


class FileUploadRequest(BaseModel):
    """Request model for file uploads with safety validation."""
    filename: str = Field(..., min_length=1, max_length=255)
    content_type: str = Field(..., description="MIME type of the file")
    file_size: int = Field(..., ge=1, le=50*1024*1024, description="File size in bytes")

    @validator('filename')
    def validate_filename_safety(cls, v) -> str:
        """Validate filename for path traversal and safety."""
        import os.path
        # Remove any path separators
        filename = os.path.basename(v)
        # Check for dangerous patterns
        dangerous_patterns = ['..', '/', '\\', ':', '*', '?', '"', '<', '>', '|']
        for pattern in dangerous_patterns:
            if pattern in filename:
                raise ValueError(f'Filename contains dangerous character: {pattern}')
        return filename

    @validator('content_type')
    def validate_content_type(cls, v) -> str:
        """Validate allowed content types."""
        allowed_types = [
            'image/jpeg', 'image/png', 'image/gif',
            'audio/wav', 'audio/mp3', 'audio/ogg',
            'text/plain', 'application/json'
        ]
        if v not in allowed_types:
            raise ValueError(f'Content type not allowed: {v}')
        return v


# Response models for consistent API responses
class APIResponse(BaseModel):
    """Standard API response wrapper."""
    success: bool = Field(..., description="Request success status")
    message: str = Field(..., description="Response message")
    data: Optional[Any] = Field(None, description="Response data")
    errors: Optional[List[str]] = Field(None, description="Error details")
    timestamp: datetime = Field(default_factory=datetime.utcnow)


class ChildSafetyResponse(BaseModel):
    """Response model for child safety validations."""
    safe: bool = Field(..., description="Content is child-safe")
    safety_score: float = Field(..., ge=0.0, le=1.0, description="Safety confidence score")
    reasons: Optional[List[str]] = Field(None, description="Safety assessment reasons")
    recommended_action: Optional[str] = Field(None, description="Recommended action if unsafe")