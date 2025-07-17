from abc import ABC, abstractmethod
from typing import Optional

class TextToSpeechService(ABC):
    @abstractmethod
    async def generate_speech(self, text: str, voice_id: str, emotion: Optional[str]=None) -> bytes:
        """Generates speech audio from text."""
        pass
