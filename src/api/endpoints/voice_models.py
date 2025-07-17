from typing import Any, Optional
from pydantic import BaseModel, Field

from src.common.constants import (
    MAX_CHILD_ID_LENGTH,
    MAX_CHILD_AGE,
    MIN_CHILD_AGE,
)


class VoiceResponse(BaseModel):
    """Response model for voice processing."""

    success: bool
    message: str
    audio_url: str | None = None
    transcript: str | None = None
    safety_score: float = Field(ge=0, le=1)
    processing_time_ms: int


class VoiceProcessingRequest(BaseModel):
    """Request model for voice processing."""

    child_id: str = Field(..., min_length=1, max_length=MAX_CHILD_ID_LENGTH)
    child_age: int = Field(..., ge=MIN_CHILD_AGE, le=MAX_CHILD_AGE)
    message_text: str | None = None
    voice_preference: str = Field(
        default="friendly",
        description="Preferred voice style for the AI response.",
    )


class AudioValidationResult(BaseModel):
    valid: bool
    error: str | None = None
    size: int | None = None
    format: str | None = None


class SpeechToTextResult(BaseModel):
    success: bool
    transcript: str | None = None
    safety_score: float = Field(ge=0, le=1)
    child_appropriate: bool
    processing_time_ms: int
    moderation_flags: list[str] | None = None
    error: str | None = None


class TextToSpeechResult(BaseModel):
    success: bool
    audio_data: bytes | None = None
    safety_score: float = Field(ge=0, le=1)
    child_appropriate: bool
    processing_time_ms: int
    voice_used: str | None = None
    error: str | None = None
