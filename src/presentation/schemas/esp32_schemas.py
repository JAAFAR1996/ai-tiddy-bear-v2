from uuid import UUID

from pydantic import BaseModel


class ESP32AudioRequestSchema(BaseModel):
    # Base64 encoded audio data
    format: str = "wav"
    child_id: UUID
    audio_data: str


class ESP32TextResponseSchema(BaseModel):
    child_id: UUID
    response_text: str
    audio_response_url: str | None = None
