import asyncio
import io

from fastapi import HTTPException, UploadFile

from src.application.interfaces.safety_monitor import SafetyMonitor
from src.domain.value_objects.safety_level import SafetyLevel
from src.infrastructure.config.settings import Settings
from src.infrastructure.logging_config import get_logger
from src.presentation.schemas.voice_schemas import (
    AudioValidationResult,
    SpeechToTextResult,
    TextToSpeechResult,
)

try:
    from pydub import AudioSegment
except ImportError:
    AudioSegment = None
from typing import Optional


class STTServiceNotConfiguredError(RuntimeError):
    def __init__(self):
        super().__init__(
            "Production STT service not configured. Cannot transcribe audio."
        )


class TTSServiceNotConfiguredError(RuntimeError):
    def __init__(self):
        super().__init__(
            "Production TTS service not configured. Cannot synthesize audio."
        )


"""Provides services for voice-related functionalities.

This module defines the `VoiceService` responsible for processing audio from
devices like ESP32, and managing voice-related features such as Whisper model
integration. It aims to provide robust voice interaction capabilities.
"""


class VoiceService:
    """Production voice processing service with child safety features.

    This service provides speech-to-text and text-to-speech capabilities
    with built-in COPPA compliance and content moderation.
    """

    def __init__(self, settings: Settings, safety_monitor: SafetyMonitor) -> None:
        """Initializes the VoiceService with provided settings.

        Args:
            settings: Application settings for audio and safety configurations.
            safety_monitor: The SafetyMonitor instance for comprehensive
                content validation.

        """
        self.settings = settings
        self.safety_monitor = safety_monitor
        self.supported_formats = self.settings.audio.SUPPORTED_AUDIO_FORMATS.split(",")
        self.max_audio_duration = self.settings.audio.MAX_AUDIO_DURATION_SECONDS
        self.max_file_size_mb = self.settings.audio.MAX_FILE_SIZE_MB
        self.logger = get_logger(__name__, component="voice_service")
        self.stt_service: Optional[object] = None
        self.tts_service: Optional[object] = None

    async def validate_audio_file(self, file: UploadFile) -> AudioValidationResult:
        """
        Validate uploaded audio file for child safety (حقيقي: تحقق من المدة والصيغة والحجم).
        """
        if not file.content_type or file.content_type not in self.supported_formats:
            return AudioValidationResult(
                valid=False,
                error=f"Unsupported audio format: {file.content_type}",
            )

        # اقرأ الملف بالكامل في الذاكرة (مطلوب للتحليل)
        file_bytes = await file.read()
        file_size = len(file_bytes)
        if file_size > self.max_file_size_mb * 1024 * 1024:
            return AudioValidationResult(valid=False, error="File size exceeds limit.")

        # تحقق من مدة الصوت باستخدام pydub إذا كانت متوفرة
        duration_seconds = None
        if AudioSegment is not None:
            try:
                audio = AudioSegment.from_file(io.BytesIO(file_bytes))
                duration_seconds = audio.duration_seconds
            except Exception as e:
                self.logger.exception("Error reading audio file for duration: %s", e)
                return AudioValidationResult(
                    valid=False, error="Invalid or corrupted audio file."
                )
        else:
            self.logger.warning(
                "pydub not installed: cannot validate audio duration. Skipping duration check."
            )

        if duration_seconds is not None and duration_seconds > self.max_audio_duration:
            return AudioValidationResult(
                valid=False,
                error=(
                    f"Audio duration exceeds limit: {duration_seconds:.2f}s > "
                    f"{self.max_audio_duration}s"
                ),
            )

        return AudioValidationResult(
            valid=True, error=None, size=file_size, format=file.content_type
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
            # تحقق من وجود خدمة STT فعلية
            if self.stt_service is None:
                self.logger.critical(
                    "No production STT service configured. Cannot transcribe audio."
                )
                raise STTServiceNotConfiguredError()
            transcript = await self.stt_service.transcribe(
                audio_file, child_age=child_age
            )

            # Perform content safety analysis on the transcript
            safety_result = await self.safety_monitor.check_content_safety(
                transcript,
                child_age=child_age,
            )

            if getattr(safety_result, "risk_level", None) not in [
                SafetyLevel.HIGH,
                SafetyLevel.CRITICAL,
            ]:
                end_time = asyncio.get_event_loop().time()
                processing_time_ms = int((end_time - start_time) * 1000)
                return SpeechToTextResult(
                    success=True,
                    transcript=transcript,
                    safety_score=getattr(safety_result, "overall_risk_level", 0),
                    child_appropriate=True,
                    processing_time_ms=processing_time_ms,
                    moderation_flags=getattr(safety_result, "analysis_details", None),
                )
            else:
                self.logger.warning(
                    "STT content blocked: Unsafe content detected for child age %s. "
                    "Transcript: '%s...' Reason: %s",
                    child_age,
                    transcript[:50],
                    getattr(safety_result, "analysis_details", None),
                )
                return SpeechToTextResult(
                    success=False,
                    transcript="Content blocked due to safety concerns.",
                    safety_score=getattr(safety_result, "overall_risk_level", 0),
                    child_appropriate=False,
                    processing_time_ms=0,
                    moderation_flags=getattr(safety_result, "analysis_details", None),
                    error="Content not appropriate for child.",
                )
        except Exception as e:
            self.logger.exception("Error during speech-to-text processing: %s", e)
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

            if getattr(safety_result, "risk_level", None) in [
                SafetyLevel.HIGH,
                SafetyLevel.CRITICAL,
            ]:
                self.logger.warning(
                    "TTS content blocked: Unsafe content detected for child age %s. "
                    "Text: '%s...' Reason: %s",
                    child_age,
                    text[:50],
                    getattr(safety_result, "analysis_details", None),
                )
                return TextToSpeechResult(
                    success=False,
                    child_appropriate=False,
                    safety_score=getattr(safety_result, "overall_risk_level", 0),
                    error="Content not appropriate for child.",
                    moderation_flags=getattr(safety_result, "analysis_details", None),
                    audio_data=b"",
                    voice_used="N/A",
                    processing_time_ms=0,
                )

            # تحقق من وجود خدمة TTS فعلية
            if self.tts_service is None:
                self.logger.critical(
                    "No production TTS service configured. Cannot synthesize audio."
                )
                raise TTSServiceNotConfiguredError()
            audio_data, voice_used = await self.tts_service.synthesize(
                text, child_age=child_age, voice_preference=voice_preference
            )

            end_time = asyncio.get_event_loop().time()
            processing_time_ms = int((end_time - start_time) * 1000)

            return TextToSpeechResult(
                success=True,
                audio_data=audio_data,
                safety_score=getattr(safety_result, "overall_risk_level", 0),
                child_appropriate=True,
                processing_time_ms=processing_time_ms,
                voice_used=voice_used,
            )
        except Exception as e:
            self.logger.exception("Error during text-to-speech processing: %s", e)
            return TextToSpeechResult(success=False, error=str(e))
