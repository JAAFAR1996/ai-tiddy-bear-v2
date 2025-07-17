"""
Provides services for converting audio data into text transcriptions.

This module defines the `TranscriptionService` responsible for handling
speech-to-text operations, including audio format validation, transcription
with fallback mechanisms, and listing supported languages. It aims to provide
accurate and reliable transcription for various audio inputs.
"""

import logging
from dataclasses import dataclass
from typing import Any, Dict, List

from src.application.services.transcription_models import TranscriptionResult
from src.application.interfaces.ai_provider import (
    AIProvider,
)  # Assuming AIProvider can handle ASR
from src.infrastructure.logging_config import get_logger
from src.application.exceptions.service_unavailable_error import ServiceUnavailableError
from src.application.exceptions.invalid_input_error import InvalidInputError

logger = get_logger(__name__, component="transcription_service")


class TranscriptionService:
    """Service for transcribing audio data to text."""

    def __init__(
        self,
        ai_provider: AIProvider,
        logger: logging.Logger = logger,
    ) -> None:
        """
        Initializes the TranscriptionService with necessary dependencies.

        Args:
            ai_provider: AI provider for speech-to-text functionality.
            logger: Logger instance for logging service operations.
        """
        self.ai_provider = ai_provider
        self.logger = logger

    async def transcribe_audio(self, audio_data: bytes) -> str:
        """
        Transcribes audio data to text using the AI provider.

        Args:
            audio_data: The audio data in bytes.

        Returns:
            The transcribed text.
        """
        self.logger.info("Initiating audio transcription via AI provider.")
        try:
            transcribed_text = await self.ai_provider.transcribe_audio(audio_data)
            self.logger.info("Audio transcription successful.")
            return transcribed_text
        except Exception as e:
            self.logger.error(
                f"Error during audio transcription: {e}",
                exc_info=True)
            raise ServiceUnavailableError(
                "Failed to transcribe audio due to an external service error."
            ) from e

    async def transcribe_with_fallback(
        self, audio_data: bytes, language: str, retries: int = 2
    ) -> TranscriptionResult:
        """
        Transcribes audio data with retry and fallback mechanisms.

        Args:
            audio_data: The audio data in bytes.
            language: The language of the audio (used for primary transcription).
            retries: Number of retry attempts for primary transcription.

        Returns:
            A TranscriptionResult object, potentially with a fallback message if transcription fails.
        """
        self.logger.info(
            f"Attempting transcription with fallback (retries: {retries})."
        )
        for attempt in range(retries + 1):
            try:
                transcribed_text = await self.ai_provider.transcribe_audio(audio_data)
                self.logger.info(
                    f"Transcription successful on attempt {attempt + 1}.")
                # In a real scenario, this would populate all
                # TranscriptionResult fields
                return TranscriptionResult(
                    transcribed_text, language, 1.0, "primary", 0, 0, [], {}
                )
            except ServiceUnavailableError as e:
                self.logger.warning(
                    f"Primary transcription failed (attempt {attempt + 1}/{retries + 1}): {e}"
                )
                if attempt == retries:
                    self.logger.error(
                        "All transcription attempts failed. Returning fallback response."
                    )
                    return TranscriptionResult(
                        "I'm sorry, I couldn't transcribe the audio. Please try again.",
                        language,
                        0.0,
                        "fallback_error",
                        0,
                        0,
                        [],
                        {},
                    )
            except Exception as e:
                self.logger.critical(
                    f"Unexpected error during transcription (attempt {attempt + 1}/{retries + 1}): {e}",
                    exc_info=True,
                )
                if attempt == retries:
                    return TranscriptionResult(
                        "An unexpected error occurred during audio processing. Please try again.",
                        language,
                        0.0,
                        "fallback_critical_error",
                        0,
                        0,
                        [],
                        {},
                    )
        # Should not be reached, but for type hinting completeness
        return TranscriptionResult("", "", 0.0, "", 0, 0, [], {})

    async def validate_audio_format(self, audio_data: bytes) -> bool:
        """
        Validates the format and basic integrity of the audio data.

        Args:
            audio_data: The audio data in bytes.

        Returns:
            True if the audio format is valid, False otherwise.

        Raises:
            InvalidInputError: If the audio data is invalid or in an unsupported format.
        """
        self.logger.info("Validating audio format.")
        # Basic validation: check if audio data is not empty
        if not audio_data:
            self.logger.warning("Audio data is empty.")
            raise InvalidInputError("Audio data cannot be empty.")

        # Further validation could include:
        # 1. Checking magic numbers for known formats (e.g., WAV, MP3)
        #    e.g., if audio_data.startswith(b'RIFF') and audio_data[8:12] == b'WAVE': ...
        # 2. Using a dedicated audio library (e.g., pydub, audioread) to parse headers
        # 3. Size limits to prevent DoS attacks
        # For now, we assume a basic binary check is sufficient until specific
        # formats are defined.
        if len(audio_data) < 100:  # Example: Minimum size for a valid audio file
            self.logger.warning(
                f"Audio data too small: {len(audio_data)} bytes.")
            raise InvalidInputError(
                "Audio data is too short to be a valid audio file.")

        self.logger.info("Audio format validation successful (basic check).")
        return True

    def get_supported_languages(self) -> list[str]:
        """
        Gets a list of supported languages for transcription.

        Returns:
            A list of language codes (e.g., ["en-US", "es-ES"]).
        """
        # In a real system, this could be dynamic from AIProvider or config service.
        # For now, providing a common set of supported languages.
        return ["en-US", "es-ES", "fr-FR", "de-DE", "zh-CN"]
