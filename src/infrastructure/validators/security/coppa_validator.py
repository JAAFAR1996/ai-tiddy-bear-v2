"""COPPA compliance validator."""
from datetime import date, datetime
from typing import Optional
from dataclasses import dataclass
from enum import Enum


class COPPAValidator:
    """COPPA compliance validation."""

    def validate_age(self, birth_date: date) -> bool:
        """Validate if child meets COPPA age requirements."""
        age = (date.today() - birth_date).days / 365.25
        return age >= 3

    def requires_consent(self, age: int) -> bool:
        """Check if parental consent is required."""
        return age < 13


@dataclass
class COPPAValidationResult:
    is_coppa_subject: bool
    reason: Optional[str] = None
    age: Optional[int] = None
    details: Optional[dict] = None


class COPPAValidatorLevel(Enum):
    UNDER_COPPA = "under_coppa"
    COPPA_TRANSITION = "coppa_transition"
    GENERAL_PROTECTION = "general_protection"


# Singleton instance
coppa_validator = COPPAValidator()
