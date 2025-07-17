"""AI Service Interface for Domain Layer
This interface defines the contract for AI services without creating
dependencies on infrastructure implementations.
"""

from abc import ABC, abstractmethod
from typing import Any


class AIServiceInterface(ABC):
    """Interface for AI service implementations."""

    @abstractmethod
    async def generate_response(
        self,
        prompt: str,
        child_context: dict[str, Any],
        safety_level: str = "strict",
    ) -> dict[str, Any]:
        """Generate AI response for child interaction.

        Args:
            prompt: Child's input prompt
            child_context: Context about the child(age, preferences, etc.)
            safety_level: Safety filtering level

        Returns:
            Dictionary with response and safety metrics

        """

    @abstractmethod
    async def assess_content_safety(self, content: str) -> dict[str, Any]:
        """Assess content safety for COPPA compliance.

        Args:
            content: Content to assess

        Returns:
            Safety assessment with score and recommendations

        """
