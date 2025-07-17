from abc import ABC, abstractmethod


class TextToSpeechService(ABC):
    @abstractmethod
    async def generate_speech(
        self,
        text: str,
        voice_id: str,
        emotion: str | None = None,
    ) -> bytes:
        """Generates speech audio from text."""
