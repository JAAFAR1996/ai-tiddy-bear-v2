"""Child Age Value Object - Domain layer representation of child age with validation.

This module provides age-related value objects for the domain layer,
ensuring COPPA compliance and age-appropriate content filtering.
"""

from dataclasses import dataclass
from enum import Enum


class AgeCategory(str, Enum):
    """Age categories for content filtering and interaction customization."""

    TODDLER = "toddler"  # 2-3 years
    PRESCHOOL = "preschool"  # 4-5 years
    EARLY_CHILD = "early_child"  # 6-8 years
    MIDDLE_CHILD = "middle_child"  # 9-11 years
    PRETEEN = "preteen"  # 12-13 years


@dataclass(frozen=True)
class ChildAge:
    """Child Age Value Object
    Represents a child's age with COPPA compliance validation
    and age-appropriate content categorization.
    """

    years: int
    months: int | None = None

    def __post_init__(self) -> None:
        """Validate age constraints."""
        if self.years < 2:
            raise ValueError("Children under 2 years are not supported")
        if self.years > 13:
            raise ValueError(
                "COPPA compliance: Children over 13 require different handling",
            )
        if self.months is not None and (self.months < 0 or self.months > 11):
            raise ValueError("Months must be between 0 and 11")

    @property
    def total_months(self) -> int:
        """Total age in months."""
        return self.years * 12 + (self.months or 0)

    @property
    def category(self) -> AgeCategory:
        """Age category for content filtering."""
        if self.years <= 3:
            return AgeCategory.TODDLER
        if self.years <= 5:
            return AgeCategory.PRESCHOOL
        if self.years <= 8:
            return AgeCategory.EARLY_CHILD
        if self.years <= 11:
            return AgeCategory.MIDDLE_CHILD
        return AgeCategory.PRETEEN

    @property
    def is_coppa_protected(self) -> bool:
        """Check if child is under COPPA protection (under 13)."""
        return self.years < 13

    @property
    def requires_parental_consent(self) -> bool:
        """Check if parental consent is required."""
        return self.is_coppa_protected

    @property
    def max_session_minutes(self) -> int:
        """Recommended maximum session length in minutes."""
        if self.years <= 3:
            return 10
        if self.years <= 5:
            return 15
        if self.years <= 8:
            return 30
        if self.years <= 11:
            return 45
        return 60

    @property
    def content_complexity_level(self) -> int:
        """Content complexity level (1-5)."""
        if self.years <= 3:
            return 1
        if self.years <= 5:
            return 2
        if self.years <= 8:
            return 3
        if self.years <= 11:
            return 4
        return 5

    @property
    def recommended_topics(self) -> list[str]:
        """Age-appropriate topic recommendations."""
        base_topics = ["animals", "colors", "shapes", "family"]
        if self.years >= 4:
            base_topics.extend(["stories", "numbers", "letters"])
        if self.years >= 6:
            base_topics.extend(["science", "nature", "friendship"])
        if self.years >= 8:
            base_topics.extend(["geography", "history", "culture"])
        if self.years >= 10:
            base_topics.extend(["technology", "environment", "creativity"])
        return base_topics

    @property
    def safety_restrictions(self) -> dict[str, bool]:
        """Safety restrictions by category."""
        return {
            "no_personal_info": True,
            "no_scary_content": self.years < 8,
            "simple_language": self.years < 6,
            "short_responses": self.years < 8,
            "positive_only": self.years < 5,
            "educational_focus": True,
            "parental_oversight": self.is_coppa_protected,
        }

    def is_appropriate_for_content(self, content_age_rating: int) -> bool:
        """Check if content is appropriate for this age."""
        return self.years >= content_age_rating

    def get_interaction_guidelines(self) -> dict[str, str]:
        """Get age-specific interaction guidelines."""
        guidelines = {
            "tone": "friendly and encouraging",
            "vocabulary": "simple and clear",
            "response_length": "short",
            "educational_level": "basic",
        }
        if self.years >= 6:
            guidelines.update(
                {
                    "vocabulary": "age-appropriate with explanations",
                    "response_length": "medium",
                    "educational_level": "elementary",
                },
            )
        if self.years >= 9:
            guidelines.update(
                {
                    "vocabulary": "expanded with learning opportunities",
                    "response_length": "detailed when needed",
                    "educational_level": "intermediate",
                },
            )
        if self.years >= 12:
            guidelines.update(
                {
                    "vocabulary": "mature but supervised",
                    "response_length": "comprehensive",
                    "educational_level": "advanced",
                },
            )
        return guidelines

    @classmethod
    def from_years(cls, years: int) -> "ChildAge":
        """Create ChildAge from years only."""
        return cls(years=years)

    @classmethod
    def from_months(cls, total_months: int) -> "ChildAge":
        """Create ChildAge from total months."""
        years = total_months // 12
        months = total_months % 12
        return cls(years=years, months=months)

    def __str__(self) -> str:
        if self.months:
            return f"{self.years} years, {self.months} months"
        return f"{self.years} years"

    def __repr__(self) -> str:
        return f"ChildAge(years={self.years}, months={self.months})"


# Note: API serialization models should be defined in the infrastructure layer
# to avoid external library dependencies in the domain layer
# Factory functions for common age ranges
def create_toddler_age(years: int = 3) -> ChildAge:
    """Create toddler age (2-3 years)."""
    if not 2 <= years <= 3:
        raise ValueError("Toddler age must be 2-3 years")
    return ChildAge.from_years(years)


def create_preschool_age(years: int = 5) -> ChildAge:
    """Create preschool age (4-5 years)."""
    if not 4 <= years <= 5:
        raise ValueError("Preschool age must be 4-5 years")
    return ChildAge.from_years(years)


def create_school_age(years: int = 8) -> ChildAge:
    """Create school age (6-11 years)."""
    if not 6 <= years <= 11:
        raise ValueError("School age must be 6-11 years")
    return ChildAge.from_years(years)


def create_preteen_age(years: int = 12) -> ChildAge:
    """Create preteen age (12-13 years)."""
    if not 12 <= years <= 13:
        raise ValueError("Preteen age must be 12-13 years")
    return ChildAge.from_years(years)
