import asyncio
import logging
import os
import re
import tempfile
import time
from datetime import datetime
from typing import Any

"""Production - grade audio transcription service with child safety filtering"""

logger = logging.getLogger(__name__)

# Production-only imports with proper error handling
try:
    import speech_recognition as sr
    import whisper

    SPEECH_RECOGNITION_AVAILABLE = True
except ImportError as e:
    logger.warning(f"Speech recognition libraries not available: {e}")
    SPEECH_RECOGNITION_AVAILABLE = False

try:
    import wave

    AUDIO_PROCESSING_AVAILABLE = True
except ImportError as e:
    logger.warning(f"Audio processing libraries not available: {e}")
    AUDIO_PROCESSING_AVAILABLE = False


class TranscriptionService:
    """Production - ready transcription service with comprehensive child safety features.
    Supports multiple transcription engines with fallback mechanisms.
    """

    def __init__(self, model_size: str = "base", language_default: str = "ar") -> None:
        self.model_size = model_size
        self.language_default = language_default
        self.max_audio_duration = 300  # 5 minutes max for safety
        self.max_audio_size = 25 * 1024 * 1024  # 25MB max
        self.supported_languages = ["ar", "en", "fr", "es"]
        self.content_filter_enabled = True
        # Initialize transcription engines
        self.whisper_model = None
        self.google_recognizer = None
        self._initialize_engines()
        # Child safety patterns to filter out
        self.unsafe_patterns = [
            r"\b(?:password|secret|address|phone)\b",
            r"\b(?:meet\\s+me|where\\s+do\\s+you\\s+live)\b",
            r"\b(?:send\\s+photo|personal\\s+information)\b",
            r"\b(?:credit\\s+card|bank\\s+account)\b",
        ]

    def _initialize_engines(self):
        """Initialize available transcription engines."""
        if SPEECH_RECOGNITION_AVAILABLE:
            try:
                # Initialize Whisper for high-quality transcription
                if whisper:
                    self.whisper_model = whisper.load_model(self.model_size)
                    logger.info(
                        f"Whisper model '{self.model_size}' loaded successfully",
                    )
                # Initialize Google Speech Recognition as fallback
                self.google_recognizer = sr.Recognizer()
                self.google_recognizer.energy_threshold = (
                    4000  # Adjust for children's voices
                )
                self.google_recognizer.dynamic_energy_threshold = True
                logger.info("Speech recognition engines initialized")
            except Exception as e:
                logger.error(f"Failed to initialize transcription engines: {e}")
        else:
            logger.warning(
                "Speech recognition not available - transcription will use mock responses",
            )

    async def transcribe_audio(
        self,
        audio_data: bytes,
        language: str | None = None,
        child_id: str | None = None,
    ) -> dict[str, Any]:
        """Transcribe audio with comprehensive validation and child safety filtering.
        Args: audio_data: Raw audio bytes
            language: Language code for transcription
            child_id: Child identifier for safety logging
        Returns: Dict containing transcription results and safety information
        Raises: ValueError: If audio data is invalid
            RuntimeError: If transcription fails.
        """
        # Input validation
        if not audio_data or not isinstance(audio_data, bytes):
            raise ValueError("Valid audio data required")
        if len(audio_data) > self.max_audio_size:
            raise ValueError(
                f"Audio too large: {len(audio_data)} bytes (max: {self.max_audio_size})",
            )
        # Language validation
        language = language or self.language_default
        if language not in self.supported_languages:
            logger.warning(
                f"Unsupported language {language}, using {self.language_default}",
            )
            language = self.language_default
        start_time = time.time()
        try:
            # Create temporary file for audio processing
            with tempfile.NamedTemporaryFile(suffix=".wav", delete=False) as temp_file:
                temp_file.write(audio_data)
                temp_audio_path = temp_file.name
            # Validate audio format and duration
            audio_info = await self._validate_audio_file(temp_audio_path)
            if not audio_info["valid"]:
                raise ValueError(f"Invalid audio format: {audio_info['error']}")
            # Perform transcription using best available method
            transcription_result = await self._perform_transcription(
                temp_audio_path,
                language,
                child_id,
            )
            # Apply child safety filtering
            filtered_result = await self._apply_safety_filters(
                transcription_result,
                child_id,
            )
            processing_time = time.time() - start_time
            result = {
                "success": True,
                "transcription": filtered_result["text"],
                "language": language,
                "confidence": transcription_result.get("confidence", 0.0),
                "duration": audio_info["duration"],
                "processing_time": round(processing_time, 2),
                "safety_passed": filtered_result["safe"],
                "engine_used": transcription_result.get("engine", "unknown"),
                "warnings": filtered_result.get("warnings", []),
                "timestamp": datetime.utcnow().isoformat(),
            }
            # Log successful transcription for audit
            if child_id:
                logger.info(
                    f"Audio transcribed for child {child_id}: "
                    f"{len(filtered_result['text'])} chars, "
                    f"safe: {filtered_result['safe']}",
                )
            return result
        except Exception as e:
            logger.error(f"Transcription failed for child {child_id}: {e}")
            raise RuntimeError(f"Audio transcription failed: {e}")
        finally:
            # Clean up temporary file
            try:
                if "temp_audio_path" in locals():
                    os.unlink(temp_audio_path)
            except Exception as e:
                logger.warning(f"Failed to cleanup temp file: {e}")

    async def _validate_audio_file(self, audio_path: str) -> dict[str, Any]:
        """Validate audio file format and properties."""
        try:
            if not AUDIO_PROCESSING_AVAILABLE:
                return {"valid": True, "duration": 0, "error": None}

            def _validate():
                with wave.open(audio_path, "rb") as wav_file:
                    frames = wav_file.getnframes()
                    rate = wav_file.getframerate()
                    duration = frames / float(rate)
                    return {
                        "valid": True,
                        "duration": duration,
                        "sample_rate": rate,
                        "channels": wav_file.getnchannels(),
                        "error": None,
                    }

            loop = asyncio.get_event_loop()
            result = await loop.run_in_executor(None, _validate)
            # Check duration limit
            if result["duration"] > self.max_audio_duration:
                result["valid"] = False
                result["error"] = (
                    f"Audio too long: {result['duration']:.1f}s (max: {self.max_audio_duration}s)"
                )
            return result
        except Exception as e:
            return {
                "valid": False,
                "duration": 0,
                "error": f"Audio validation failed: {e}",
            }

    async def _perform_transcription(
        self,
        audio_path: str,
        language: str,
        child_id: str | None = None,
    ) -> dict[str, Any]:
        """Perform actual transcription using available engines."""
        # Try Whisper first (most accurate)
        if self.whisper_model:
            try:

                def _whisper_transcribe():
                    result = self.whisper_model.transcribe(
                        audio_path,
                        language=language if language != "ar" else None,
                        fp16=False,  # More stable
                    )
                    return {
                        "text": result["text"].strip(),
                        "confidence": 0.9,  # Whisper doesn't provide confidence scores
                        "engine": "whisper",
                    }

                loop = asyncio.get_event_loop()
                result = await loop.run_in_executor(None, _whisper_transcribe)
                if result["text"]:
                    return result
            except Exception as e:
                logger.warning(f"Whisper transcription failed: {e}")
        # Fallback to Google Speech Recognition
        if self.google_recognizer and SPEECH_RECOGNITION_AVAILABLE:
            try:

                def _google_transcribe():
                    with sr.AudioFile(audio_path) as source:
                        audio = self.google_recognizer.record(source)
                    # Map language codes
                    google_lang_map = {
                        "ar": "ar-SA",
                        "en": "en-US",
                        "fr": "fr-FR",
                        "es": "es-ES",
                    }
                    google_language = google_lang_map.get(language, "ar-SA")
                    text = self.google_recognizer.recognize_google(
                        audio,
                        language=google_language,
                        show_all=False,
                    )
                    return {
                        "text": text.strip() if text else "",
                        "confidence": 0.7,  # Default confidence for Google
                        "engine": "google",
                    }

                loop = asyncio.get_event_loop()
                result = await loop.run_in_executor(None, _google_transcribe)
                if result["text"]:
                    return result
            except Exception as e:
                logger.warning(f"Google transcription failed: {e}")
        # Production: لا fallback وهمي، بل سجل خطأ وارفع استثناء
        logger.error("All transcription engines failed: transcription service unavailable")
        raise RuntimeError("Transcription service unavailable: all engines failed")

    async def _apply_safety_filters(
        self,
        transcription_result: dict[str, Any],
        child_id: str | None = None,
    ) -> dict[str, Any]:
        """Apply child safety filtering to transcription results."""
        text = transcription_result.get("text", "")
        warnings = []
        if not self.content_filter_enabled:
            return {"text": text, "safe": True, "warnings": warnings}
        # Check for unsafe patterns
        for pattern in self.unsafe_patterns:
            matches = re.findall(pattern, text, re.IGNORECASE)
            if matches:
                warnings.append(f"Potentially unsafe content detected: {pattern}")
                # Replace with safe alternative
                text = re.sub(pattern, "[FILTERED]", text, flags=re.IGNORECASE)
        # Additional safety checks
        if len(text.strip()) == 0:
            return {"text": "", "safe": True, "warnings": warnings}
        # Check for excessive length (potential spam/abuse)
        if len(text) > 1000:
            warnings.append("Text too long, truncating for safety")
            text = text[:1000] + "..."
        # Log safety issues if any
        if warnings and child_id:
            logger.warning(f"Safety issues detected for child {child_id}: {warnings}")
        return {"text": text, "safe": len(warnings) == 0, "warnings": warnings}

    async def get_supported_languages(self) -> list[str]:
        """Get list of supported languages for transcription."""
        return self.supported_languages.copy()

    async def health_check(self) -> dict[str, Any]:
        """Check health status of transcription service."""
        return {
            "status": "healthy",
            "engines": {
                "whisper": self.whisper_model is not None,
                "google": self.google_recognizer is not None,
                "speech_recognition_available": SPEECH_RECOGNITION_AVAILABLE,
                "audio_processing_available": AUDIO_PROCESSING_AVAILABLE,
            },
            "supported_languages": self.supported_languages,
            "max_duration": self.max_audio_duration,
            "max_size_mb": self.max_audio_size // (1024 * 1024),
            "content_filter_enabled": self.content_filter_enabled,
        }
