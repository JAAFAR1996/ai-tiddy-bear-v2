from typing import Protocol

from src.domain.value_objects.safety_level import SafetyLevel


class SafetyValidator(Protocol):
    async def validate_text(self, text: str) -> SafetyLevel:
        ...

    async def validate_audio(self, audio_data: bytes) -> SafetyLevel:
        ...
