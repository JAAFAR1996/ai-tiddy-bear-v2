from abc import ABC, abstractmethod

from src.domain.models.safety_models import RiskLevel, SafetyAnalysisResult

SafetyLevel = RiskLevel  # Alias for clarity in some contexts


class SafetyMonitor(ABC):
    @abstractmethod
    async def check_content_safety(
        self,
        content: str,
        child_age: int = 0,
        conversation_history: list[str] | None = None,
    ) -> SafetyAnalysisResult:
        """Checks the safety of content based on various criteria."""
