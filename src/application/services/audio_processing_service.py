"""
Handles the processing of audio input and the generation of audio responses.

This service integrates speech-to-text, safety monitoring, and text-to-speech
functionalities to provide a seamless audio interaction experience. It ensures
that all audio is processed safely and efficiently.
"""

import logging
from src.infrastructure.logging_config import get_logger

from src.application.interfaces.safety_monitor import SafetyMonitor
from src.application.interfaces.speech_processor import SpeechProcessor
from src.application.interfaces.text_to_speech_service import TextToSpeechService
from src.domain.value_objects.safety_level import SafetyLevel


logger = get_logger(__name__, component="audio_processing_service")


class AudioProcessingService:
    """Service for processing audio input and generating audio responses."""

    def __init__(
        self,
        speech_processor: SpeechProcessor,
        safety_monitor: SafetyMonitor,
        tts_service: TextToSpeechService,
    ):
        """
        Initializes the audio processing service.

        Args:
            speech_processor: The speech-to-text processor.
            safety_monitor: The safety monitor for audio content.
            tts_service: The text-to-speech service.
        """
        self.speech_processor = speech_processor
        self.safety_monitor = safety_monitor
        self.tts_service = tts_service

    async def process_audio_input(
        self, audio_data: bytes, language: str
    ) -> tuple[str, SafetyLevel]:
        """
        Processes incoming audio data.

        Args:
            audio_data: The audio data to process.
            language: The language of the audio.

        Returns:
            A tuple containing the transcription and the safety level.
        """
        transcription = await self.speech_processor.speech_to_text(audio_data, language)
        safety_level = await self.safety_monitor.check_audio_safety(audio_data)
        return transcription, safety_level

    async def generate_audio_response(self, text: str, voice_id: str) -> bytes:
        """
        Generates an audio response from text.

        Args:
            text: The text to convert to speech.
            voice_id: The ID of the voice to use.

        Returns:
            The generated audio data.
        """
        try:
            return await self.tts_service.text_to_speech(text, voice_id)
        except Exception as e:
            self.logger.error(
                f"Failed to generate audio response for text: '{text[:50]}...' with voice_id: {voice_id}. Error: {e}",
                exc_info=True,
            )
            return b""
