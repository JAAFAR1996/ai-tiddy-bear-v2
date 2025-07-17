from pydantic import BaseModel, Field


class VoiceResponse(BaseModel):
    """Response model for voice processing."""

    success: bool
    message: str
    transcript: str | None = None
    safety_score: float = Field(ge=0, le=1)
    processing_time_ms: int


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
