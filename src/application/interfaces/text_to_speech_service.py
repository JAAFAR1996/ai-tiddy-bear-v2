from abc import ABC, abstractmethod
from typing import Optional


class TextToSpeechService(ABC):
    """Abstract base class for text-to-speech services"""

    @abstractmethod
    async def generate_speech(
        self,
        text: str,
        voice_id: str,
        emotion: Optional[str] = None,
    ) -> bytes:
        """Generate speech audio from text

        Args:
            text: The text to convert to speech
            voice_id: Identifier for the voice to use
            emotion: Optional emotion to apply to the speech

        Returns:
            Audio data as bytes
        """

    @abstractmethod
    async def list_voices(self) -> list[dict]:
        """List available voices

        Returns:
            List of voice information dictionaries
        """

    @abstractmethod
    async def health_check(self) -> bool:
        """Check if the TTS service is healthy

        Returns:
            True if service is healthy, False otherwise
        """
