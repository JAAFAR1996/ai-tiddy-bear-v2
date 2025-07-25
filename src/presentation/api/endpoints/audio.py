# Standard library imports
import io
import json

# Third-party imports
from fastapi import APIRouter, Depends, File, UploadFile
from fastapi.responses import StreamingResponse

# Local imports
from src.application.services.ai.modules.transcription_service import (
    TranscriptionService,
)
from src.application.services.device.audio_processing_service import (
    AudioProcessingService,
)
from src.infrastructure.security.auth.real_auth_service import (
    UserInfo,
    get_current_user,
)
from src.presentation.api.dependencies import get_audio_processing_service

router = APIRouter()


@router.post(
    "/transcribe",
    response_class=StreamingResponse,
    summary="Transcribe audio file",
    description="Transcribes an uploaded audio file and processes it to generate a child-safe AI response.",
)
async def transcribe_audio(
    audio_file: UploadFile = File(
        ..., description="The audio file to transcribe (e.g., WAV, MP3)."
    ),
    voice_service: AudioProcessingService = Depends(get_audio_processing_service),
    current_user: UserInfo = Depends(get_current_user),
) -> StreamingResponse:
    """Transcribes an uploaded audio file and processes child-safe AI response."""
    try:
        # Read audio file
        audio_content = await audio_file.read()

        # Initialize transcription service
        transcription_service = TranscriptionService()

        # Transcribe audio using existing service
        result = await transcription_service.transcribe_audio(
            audio_data=audio_content,
            language="ar",  # Default language
            child_id=(
                current_user.user_id if hasattr(current_user, "user_id") else None
            ),
        )

        # Process transcription through audio processing service for safety
        transcription_text = result.get("transcription", "")

        # Use existing audio processing service to handle the transcription
        # and generate safe response
        processed_text, safety_level = await voice_service.process_audio_input(
            audio_data=audio_content, language="ar"
        )

        # Create response data
        response_data = {
            "success": True,
            "transcription": transcription_text,
            "processed_text": processed_text,
            "safety_level": (
                safety_level.value
                if hasattr(safety_level, "value")
                else str(safety_level)
            ),
            "confidence": result.get("confidence", 0.0),
            "processing_time": result.get("processing_time", 0.0),
            "child_safe": result.get("safe", True),
            "warnings": result.get("warnings", []),
        }

        # Convert to JSON bytes for streaming
        json_response = json.dumps(response_data)
        response_stream = io.BytesIO(json_response.encode("utf-8"))

        return StreamingResponse(
            response_stream,
            media_type="application/json",
            headers={"Content-Disposition": "inline; filename=transcription.json"},
        )

    except Exception as e:
        # Error response
        error_data = {
            "success": False,
            "error": str(e),
            "transcription": "",
            "child_safe": False,
        }

        json_response = json.dumps(error_data)
        response_stream = io.BytesIO(json_response.encode("utf-8"))

        return StreamingResponse(
            response_stream, media_type="application/json", status_code=500
        )
