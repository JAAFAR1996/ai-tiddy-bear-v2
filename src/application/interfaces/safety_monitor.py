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

from enum import Enum
from dataclasses import dataclass
from typing import List, Optional

class SafetyLevel(Enum):
    """Safety level enumeration."""
    SAFE = "safe"
    WARNING = "warning"
    DANGER = "danger"

@dataclass
class SafetyAnalysisResult:
    """Result of safety analysis."""
    is_safe: bool
    safety_level: SafetyLevel
    issues: List[str]
    confidence: float
    recommendations: Optional[List[str]] = None
