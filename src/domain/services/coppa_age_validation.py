"""Centralized COPPA Age Validation Service
Provides consistent age validation across the entire application for COPPA compliance.
"""

from datetime import date
from enum import Enum
from typing import Any


class AgeValidationResult(Enum):
    """Age validation results with specific meanings."""

    VALID_CHILD = "valid_child"  # Age 3-13, requires parental consent
    VALID_TEEN = "valid_teen"  # Age 13-17, may require parental consent
    VALID_ADULT = "valid_adult"  # Age 18+, no parental consent needed
    TOO_YOUNG = "too_young"  # Under 3, safety concern
    INVALID_AGE = "invalid_age"  # Invalid age data
    MISSING_BIRTHDATE = "missing_birthdate"  # No birthdate provided


class COPPAAgeValidator:
    """Centralized age validation for COPPA compliance."""

    MINIMUM_AGE = 3  # Minimum safe interaction age
    COPPA_AGE_LIMIT = 13  # COPPA applies to children under 13
    ADULT_AGE = 18  # Adult age (no parental consent needed)

    @classmethod
    def validate_age(cls, age: int | None) -> AgeValidationResult:
        """Validate age for COPPA compliance.

        Args:
            age: The child's age in years
        Returns:
            AgeValidationResult indicating the validation outcome

        """
        if age is None:
            return AgeValidationResult.INVALID_AGE
        if not isinstance(age, int) or age < 0:
            return AgeValidationResult.INVALID_AGE
        if age < cls.MINIMUM_AGE:
            return AgeValidationResult.TOO_YOUNG
        if age < cls.COPPA_AGE_LIMIT:
            return AgeValidationResult.VALID_CHILD
        if age < cls.ADULT_AGE:
            return AgeValidationResult.VALID_TEEN
        return AgeValidationResult.VALID_ADULT

    @classmethod
    def validate_birthdate(cls, birthdate: date | None) -> AgeValidationResult:
        """Validate birthdate and calculate age for COPPA compliance.

        Args:
            birthdate: The child's date of birth
        Returns:
            AgeValidationResult indicating the validation outcome

        """
        if birthdate is None:
            return AgeValidationResult.MISSING_BIRTHDATE
        if not isinstance(birthdate, date):
            return AgeValidationResult.INVALID_AGE
        # Check if birthdate is in the future
        today = date.today()
        if birthdate > today:
            return AgeValidationResult.INVALID_AGE
        # Calculate age
        age = today.year - birthdate.year
        # Adjust for birthday not yet occurred this year
        if (today.month, today.day) < (birthdate.month, birthdate.day):
            age -= 1
        return cls.validate_age(age)

    @classmethod
    def get_age_from_birthdate(cls, birthdate: date) -> int:
        """Calculate precise age from birthdate.

        Args:
            birthdate: The child's date of birth
        Returns:
            Age in years

        """
        today = date.today()
        age = today.year - birthdate.year
        # Adjust for birthday not yet occurred this year
        if (today.month, today.day) < (birthdate.month, birthdate.day):
            age -= 1
        return max(0, age)  # Ensure non-negative age

    @classmethod
    def requires_parental_consent(cls, age: int) -> bool:
        """Determine if parental consent is required based on age.

        Args:
            age: The child's age in years
        Returns:
            True if parental consent is required

        """
        validation_result = cls.validate_age(age)
        return validation_result in [
            AgeValidationResult.VALID_CHILD,
            AgeValidationResult.VALID_TEEN,
        ]

    @classmethod
    def is_coppa_applicable(cls, age: int) -> bool:
        """Determine if COPPA regulations apply based on age.

        Args:
            age: The child's age in years
        Returns:
            True if COPPA applies (under 13)

        """
        validation_result = cls.validate_age(age)
        return validation_result == AgeValidationResult.VALID_CHILD

    @classmethod
    def get_validation_details(cls, age: int | None) -> dict[str, Any]:
        """Get detailed validation information for an age.

        Args:
            age: The child's age in years
        Returns:
            Dictionary with validation details

        """
        validation_result = cls.validate_age(age)
        return {
            "age": age,
            "validation_result": validation_result.value,
            "is_valid": validation_result
            not in [
                AgeValidationResult.TOO_YOUNG,
                AgeValidationResult.INVALID_AGE,
            ],
            "requires_parental_consent": (
                cls.requires_parental_consent(age) if age else False
            ),
            "coppa_applicable": cls.is_coppa_applicable(age) if age else False,
            "can_interact": validation_result
            in [
                AgeValidationResult.VALID_CHILD,
                AgeValidationResult.VALID_TEEN,
                AgeValidationResult.VALID_ADULT,
            ],
            "safety_level": cls._get_safety_level(validation_result),
            "compliance_notes": cls._get_compliance_notes(validation_result),
        }

    @classmethod
    def _get_safety_level(cls, result: AgeValidationResult) -> str:
        """Get safety level based on validation result."""
        safety_levels = {
            AgeValidationResult.VALID_CHILD: "high_protection",
            AgeValidationResult.VALID_TEEN: "moderate_protection",
            AgeValidationResult.VALID_ADULT: "standard_protection",
            AgeValidationResult.TOO_YOUNG: "blocked",
            AgeValidationResult.INVALID_AGE: "blocked",
            AgeValidationResult.MISSING_BIRTHDATE: "blocked",
        }
        return safety_levels.get(result, "blocked")

    @classmethod
    def _get_compliance_notes(cls, result: AgeValidationResult) -> str:
        """Get compliance notes based on validation result."""
        notes = {
            AgeValidationResult.VALID_CHILD: "COPPA compliance required. Parental consent mandatory.",
            AgeValidationResult.VALID_TEEN: "Parental consent recommended. Enhanced privacy protection.",
            AgeValidationResult.VALID_ADULT: "Standard privacy protection applies.",
            AgeValidationResult.TOO_YOUNG: "Age too young for safe interaction.",
            AgeValidationResult.INVALID_AGE: "Invalid age data provided.",
            AgeValidationResult.MISSING_BIRTHDATE: "Birthdate required for age verification.",
        }
        return notes.get(result, "Unknown validation result.")


def validate_child_age(age: int | None) -> dict[str, Any]:
    """Convenience function for age validation.

    Args:
        age: The child's age in years
    Returns:
        Validation details dictionary

    """
    return COPPAAgeValidator.get_validation_details(age)


def is_age_coppa_compliant(age: int) -> bool:
    """Quick check if age requires COPPA compliance.

    Args:
        age: The child's age in years
    Returns:
        True if COPPA compliance is required

    """
    return COPPAAgeValidator.is_coppa_applicable(age)
