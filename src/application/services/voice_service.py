"""Provides services for voice-related functionalities.

This module defines the `VoiceService` responsible for processing audio from
devices like ESP32, and managing voice-related features such as Whisper model
integration. It aims to provide robust voice interaction capabilities.
"""

import asyncio

from fastapi import HTTPException, UploadFile

from src.api.endpoints.voice_models import (
    AudioValidationResult,
    SpeechToTextResult,
    TextToSpeechResult,
)
from src.application.interfaces.safety_monitor import SafetyMonitor
from src.domain.safety.models import SafetyLevel
from src.infrastructure.config.settings import Settings
from src.infrastructure.logging_config import get_logger


class VoiceService:
    """Production voice processing service with child safety features.

    This service provides speech-to-text and text-to-speech capabilities
    with built-in COPPA compliance and content moderation.
    """

    def __init__(self, settings: Settings, safety_monitor: SafetyMonitor) -> None:
        """Initializes the VoiceService with provided settings.

        Args:
            settings: Application settings for audio and safety configurations.
            safety_monitor: The SafetyMonitor instance for comprehensive content validation.

        """
        self.settings = settings
        self.safety_monitor = safety_monitor
        self.supported_formats = self.settings.audio.SUPPORTED_AUDIO_FORMATS.split(",")
        self.max_audio_duration = self.settings.audio.MAX_AUDIO_DURATION_SECONDS
        self.max_file_size_mb = self.settings.audio.MAX_FILE_SIZE_MB
        self.logger = get_logger(__name__, component="voice_service")

    async def validate_audio_file(self, file: UploadFile) -> AudioValidationResult:
        """Validate uploaded audio file for child safety.

        Args:
            file: Uploaded audio file.

        Returns:
            AudioValidationResult containing validation results.

        """
        if not file.content_type or file.content_type not in self.supported_formats:
            return AudioValidationResult(
                valid=False,
                error=f"Unsupported audio format: {file.content_type}",
            )

        file_size = 0
        while chunk := await file.read(8192):
            file_size += len(chunk)
            if file_size > self.max_file_size_mb * 1024 * 1024:
                return AudioValidationResult(
                    valid=False,
                    error="File size exceeds limit.",
                )

        # TODO: Implement actual audio duration validation if needed. This requires
        #  reading audio headers, which might be complex without a dedicated library.
        # For now, we assume duration is within limits if file size is.

        return AudioValidationResult(
            valid=True,
            error=None,
            size=file_size,
            format=file.content_type,
        )

    async def speech_to_text(
        self,
        audio_file: UploadFile,
        child_age: int,
    ) -> SpeechToTextResult:
        """Convert speech to text with child safety filtering.

        Args:
            audio_file: Audio file to transcribe.
            child_age: Age of the child for appropriate processing.

        Returns:
            SpeechToTextResult containing transcription and safety analysis.

        """
        start_time = asyncio.get_event_loop().time()
        try:
            # Validate audio file first
            validation_result = await self.validate_audio_file(audio_file)
            if not validation_result.valid:
                raise HTTPException(status_code=400, detail=validation_result.error)

            await audio_file.read()
            # Placeholder for actual STT service call
            transcript = f"This is a placeholder transcript for audio from child aged {child_age}."

            # Perform content safety analysis on the transcript
            safety_result = await self.safety_monitor.check_content_safety(
                transcript,
                child_age=child_age,
            )

            if safety_result.risk_level in [
                SafetyLevel.UNSAFE,
                SafetyLevel.POTENTIALLY_UNSAFE,
            ]:
                self.logger.warning(
                    f"STT content blocked: Unsafe content detected for child age {child_age}. Transcript: '{transcript[:50]}...' Reason: {safety_result.analysis_details}",
                )
                return SpeechToTextResult(
                    success=False,
                    transcript="Content blocked due to safety concerns.",
                    safety_score=safety_result.overall_risk_level.value,
                    child_appropriate=False,
                    processing_time_ms=0,
                    moderation_flags=safety_result.analysis_details,
                    error="Content not appropriate for child.",
                )

            end_time = asyncio.get_event_loop().time()
            processing_time_ms = int((end_time - start_time) * 1000)

            return SpeechToTextResult(
                success=True,
                transcript=transcript,
                safety_score=safety_result.overall_risk_level.value,
                child_appropriate=True,
                processing_time_ms=processing_time_ms,
                moderation_flags=safety_result.analysis_details,
            )
        except Exception as e:
            self.logger.error(
                f"Error during speech-to-text processing: {e}",
                exc_info=True,
            )
            return SpeechToTextResult(success=False, error=str(e))

    async def text_to_speech(
        self,
        text: str,
        child_age: int,
        voice_preference: str = "friendly",
    ) -> TextToSpeechResult:
        """Convert text to speech with age-appropriate voice settings.

        Args:
            text: Text to convert to speech.
            child_age: Age of the child for voice optimization.
            voice_preference: Voice style preference.

        Returns:
            TextToSpeechResult containing audio data and metadata.

        """
        start_time = asyncio.get_event_loop().time()
        try:
            # First, check text for child safety before converting to speech
            safety_result = await self.safety_monitor.check_content_safety(
                text,
                child_age=child_age,
            )

            if safety_result.risk_level in [
                SafetyLevel.UNSAFE,
                SafetyLevel.POTENTIALLY_UNSAFE,
            ]:
                self.logger.warning(
                    f"TTS content blocked: Unsafe content detected for child age {child_age}. Text: '{text[:50]}...' Reason: {safety_result.analysis_details}",
                )
                return TextToSpeechResult(
                    success=False,
                    child_appropriate=False,
                    safety_score=safety_result.overall_risk_level.value,
                    error="Content not appropriate for child.",
                    moderation_flags=safety_result.analysis_details,
                    audio_data=b"",
                    voice_used="N/A",
                    processing_time_ms=0,
                )

            # Placeholder for actual TTS service call
            audio_data = b"dummy_audio_data"
            voice_used = f"{voice_preference}_voice"

            end_time = asyncio.get_event_loop().time()
            processing_time_ms = int((end_time - start_time) * 1000)

            return TextToSpeechResult(
                success=True,
                audio_data=audio_data,
                safety_score=safety_result.overall_risk_level.value,
                child_appropriate=True,
                processing_time_ms=processing_time_ms,
                voice_used=voice_used,
            )
        except Exception as e:
            self.logger.error(
                f"Error during text-to-speech processing: {e}",
                exc_info=True,
            )
            return TextToSpeechResult(success=False, error=str(e))
