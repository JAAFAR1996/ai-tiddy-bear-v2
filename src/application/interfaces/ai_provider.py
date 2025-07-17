from typing import Any, Protocol
from uuid import UUID

from src.domain.value_objects.child_preferences import ChildPreferences


class AIProvider(Protocol):
    """Defines the interface for AI service providers."""

    async def generate_response(
        self,
        child_id: UUID,
        conversation_history: list[str],
        current_input: str,
        child_preferences: ChildPreferences,
    ) -> str: ...

    async def analyze_sentiment(self, text: str) -> float: ...

    async def analyze_emotion(self, text: str) -> str: ...

    async def analyze_toxicity(self, text: str) -> float: ...

    async def analyze_personality(
        self,
        interactions: list[dict[str, Any]],
    ) -> dict[str, Any]: ...

    async def supports_asr_model(self) -> bool: ...

    async def transcribe_audio(self, audio_data: bytes) -> str: ...

    async def evaluate_educational_value(
        self, text: str
    ) -> dict[str, Any]: ...

    async def determine_activity_type(
        self,
        text: str,
        emotion: dict[str, Any],
        session_context: dict[str, Any],
    ) -> str: ...

    async def generate_personalized_content(
        self,
        child_id: UUID,
        personality_profile: dict[str, Any],
        context: dict[str, Any],
    ) -> dict[str, Any]: ...
