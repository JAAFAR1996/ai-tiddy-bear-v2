# Standard library imports
import io
from typing import Any, Dict,
# Optional
import magic

# Third-party imports
from fastapi import APIRouter,
# Depends, File, HTTPException, UploadFile, status
from fastapi.responses
# import StreamingResponse
from fastapi.security import
# HTTPAuthorizationCredentials, HTTPBearer
from
# src.presentation.api.dependencies.auth import get_authenticated_user
#
# Local imports
from src.utils.file_validators import
# validate_audio_file

"""🎵 Audio Processing Endpoints - CHILD SAFETY
# PROTECTED
Added comprehensive authentication and COPPA compliance"""

from
# src.application.services.ai_orchestration_service import
# AIOrchestrationService
from
# src.application.services.audio_processing_service import
# AudioProcessingService
from src.infrastructure.di.container import
# container
from src.infrastructure.security.real_auth_service import
# get_current_user, UserInfo

router = APIRouter()

@router.post(
# "/transcribe",
    summary="Transcribe audio input and return a
# child-safe response",
    response_description="A streaming audio
# response or an error message.",)
async def transcribe_audio(
# audio_file: UploadFile = File(
        ..., description="The audio file
# to transcribe (e.g., WAV, MP3)."
    ),
    child_context:
# Optional[Dict[str, Any]] = Field(
        None, description="Optional
# context about the child for personalization."
    ),
    voice_service:
# AudioProcessingService = Depends(container.audio_processing_service),
# current_user: UserInfo = Depends(get_current_user),) ->
# StreamingResponse:
    """Transcribes an uploaded audio file and
# processes it to generate a child-safe AI response.
    This endpoint
# handles audio input from devices (like ESP32) or other sources,
# transcribes it using the `AudioProcessingService`, and then uses the
# `AIOrchestrationService`
    to generate an appropriate, moderated
# response. The response is streamed back as audio.
    **Security and
# Safety:**
    - Input audio is validated for type and size.
    - All AI
# interactions are routed through child-safe moderation layers.
    -
# Requires authentication via JWT.
    **Parameters:**
    - `audio_file`:
# The audio file to be transcribed. Supported formats include WAV, MP3.
# - `child_context`: A JSON object providing additional context about the
# child,
      which can be used for personalization of the AI response.
# **Responses:**
    - `200 OK`: Returns a `StreamingResponse` containing
# the audio of the AI's reply.
    - `400 Bad Request`: If the input audio
# is invalid or child context is malformed.
    - `401 Unauthorized`: If
# authentication credentials are missing or invalid.
    - `415 Unsupported
# Media Type`: If the uploaded file is not a supported audio format.
    -
# `413 Request Entity Too Large`: If the uploaded file exceeds the maximum
# allowed size.
    - `500 Internal Server Error`: If an unexpected error
# occurs during processing.
    """
    validate_audio_file(audio_file)