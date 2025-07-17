import asyncio
import logging
import io

from fastapi import APIRouter, Depends, File, Form, HTTPException, UploadFile
from fastapi.responses import Response

from src.api.endpoints.voice_models import (
    AudioValidationResult,
    SpeechToTextResult,
    TextToSpeechResult,
    VoiceProcessingRequest,
    VoiceResponse,
)
from src.application.services.voice_service import VoiceService
from src.common.constants import MAX_CHILD_AGE, MAX_CHILD_ID_LENGTH, MIN_CHILD_AGE

# Initialize FastAPI router
router = APIRouter()
logger = logging.getLogger(__name__)


@router.post(
    "/process_voice_message",
    response_model=VoiceResponse,
    summary="Process a child's voice message",
    description="Receives an audio file, transcribes it, applies safety filters, and generates an AI response.",
)
async def process_voice_message(
    child_id: str = Form(..., min_length=1, max_length=MAX_CHILD_ID_LENGTH),
    child_age: int = Form(..., ge=MIN_CHILD_AGE, le=MAX_CHILD_AGE),
    audio_file: UploadFile = File(...),
    voice_service: VoiceService = Depends(VoiceService),
):
    """
    Handles the processing of a voice message from the AI Teddy Bear.
    """
    logger.info(f"Received voice message for child_id: {child_id}")

    # Speech-to-Text
    stt_result = await voice_service.speech_to_text(audio_file, child_age)
    if not stt_result.success:
        raise HTTPException(status_code=500, detail=f"Speech-to-text failed: {stt_result.error}")

    if not stt_result.child_appropriate:
        raise HTTPException(status_code=403, detail="Content not appropriate for child.")

    # AI Response Generation (Placeholder)
    # In a real scenario, this would involve calling an AI service with the transcript
    ai_response_text = f"Hello {child_id}, you said: '{stt_result.transcript}'. This is an AI response."
    logger.info(f"Generated AI response: {ai_response_text}")

    # Text-to-Speech for AI Response
    tts_result = await voice_service.text_to_speech(ai_response_text, child_age)
    if not tts_result.success or not tts_result.audio_data:
        raise HTTPException(status_code=500, detail=f"Text-to-speech failed: {tts_result.error}")

    # Return audio directly as a response
    return Response(content=tts_result.audio_data, media_type="audio/mpeg")


@router.post(
    "/validate_audio",
    response_model=AudioValidationResult,
    summary="Validate an uploaded audio file",
    description="Validates the format and size of an audio file for compatibility.",
)
async def validate_audio_file_endpoint(
    audio_file: UploadFile = File(...),
    voice_service: VoiceService = Depends(VoiceService),
):
    """
    Validates an uploaded audio file.
    """
    logger.info(f"Received audio file for validation: {audio_file.filename}")
    validation_result = await voice_service.validate_audio_file(audio_file)
    if not validation_result.valid:
        raise HTTPException(status_code=400, detail=validation_result.error)
    return validation_result


@router.post(
    "/speech_to_text_endpoint",
    response_model=SpeechToTextResult,
    summary="Convert speech to text",
    description="Transcribes an audio file into text, applying child safety filters.",
)
async def speech_to_text_endpoint(
    child_age: int = Form(..., ge=MIN_CHILD_AGE, le=MAX_CHILD_AGE),
    audio_file: UploadFile = File(...),
    voice_service: VoiceService = Depends(VoiceService),
):
    """
    Converts speech from an audio file to text.
    """
    logger.info(f"Received audio for speech-to-text for child age: {child_age}")
    stt_result = await voice_service.speech_to_text(audio_file, child_age)
    if not stt_result.success:
        raise HTTPException(status_code=500, detail=stt_result.error)
    return stt_result


@router.post(
    "/text_to_speech_endpoint",
    response_model=TextToSpeechResult,
    summary="Convert text to speech",
    description="Converts text into an audio file, using age-appropriate voice settings.",
)
async def text_to_speech_endpoint(
    text: str = Form(..., min_length=1),
    child_age: int = Form(..., ge=MIN_CHILD_AGE, le=MAX_CHILD_AGE),
    voice_preference: str = Form("friendly"),
    voice_service: VoiceService = Depends(VoiceService),
):
    """
    Converts text to speech.
    """
    logger.info(f"Received text for text-to-speech for child age: {child_age}")
    tts_result = await voice_service.text_to_speech(text, child_age, voice_preference)
    if not tts_result.success:
        raise HTTPException(status_code=500, detail=tts_result.error)
    return tts_result 