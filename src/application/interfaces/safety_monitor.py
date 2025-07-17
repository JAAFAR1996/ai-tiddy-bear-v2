from abc import ABC, abstractmethod
from typing import List
from src.domain.safety.models import SafetyAnalysisResult, RiskLevel

SafetyLevel = RiskLevel  # Alias for clarity in some contexts

class SafetyMonitor(ABC):
    @abstractmethod
    async def check_content_safety(
        self, content: str, child_age: int = 0, conversation_history: List[str] = None
    ) -> SafetyAnalysisResult:
        """Checks the safety of content based on various criteria."""
        pass