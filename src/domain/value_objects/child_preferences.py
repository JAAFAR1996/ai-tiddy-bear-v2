"""Child Preferences Value Object - Domain Layer
This module provides child preference modeling without external dependencies,
maintaining clean domain architecture.
"""

from dataclasses import dataclass, field
from enum import Enum
from typing import Any


class AgeGroup(Enum):
    """Age groups for children with safety-appropriate categorization."""

    TODDLER = "toddler"
    PRESCHOOL = "preschool"
    EARLY_SCHOOL = "early_school"
    SCHOOL_AGE = "school_age"
    PRE_TEEN = "pre_teen"
    TEEN = "teen"

    @staticmethod
    def from_age(age: int) -> "AgeGroup":
        """Convert numeric age to appropriate age group."""
        if 0 <= age <= 2:
            return AgeGroup.TODDLER
        if 3 <= age <= 5:
            return AgeGroup.PRESCHOOL
        if 6 <= age <= 8:
            return AgeGroup.EARLY_SCHOOL
        if 9 <= age <= 12:
            return AgeGroup.SCHOOL_AGE
        if 13 <= age <= 15:
            return AgeGroup.PRE_TEEN
        return AgeGroup.TEEN


@dataclass
class ChildPreferences:
    """Value object for child preferences and settings."""

    language: str = "en"
    interests: list[str] = field(default_factory=list)
    favorite_colors: list[str] = field(default_factory=list)
    favorite_characters: list[str] = field(default_factory=list)
    story_themes: list[str] = field(default_factory=list)
    learning_pace: str = "medium"
    audio_preferences: dict[str, Any] = field(default_factory=dict)
    age_group: AgeGroup = None
    safety_level: str = "moderate"
    voice_preference: str = "child_friendly"

    def __post_init__(self):
        """Validate preferences after initialization."""
        # Validate language
        if not self.language:
            self.language = "en"

        # Validate learning pace
        valid_paces = ["slow", "medium", "fast", "adaptive"]
        if self.learning_pace not in valid_paces:
            self.learning_pace = "medium"

    @classmethod
    def create_default(cls) -> "ChildPreferences":
        """Create default preferences."""
        return cls()

    def add_interest(self, interest: str) -> None:
        """Add an interest if not already present."""
        if interest not in self.interests:
            self.interests.append(interest)

    def remove_interest(self, interest: str) -> None:
        """Remove an interest."""
        if interest in self.interests:
            self.interests.remove(interest)

    def update_language(self, language: str) -> None:
        """Update language preference."""
        self.language = language

    def update_age_group(self, age_group: AgeGroup) -> None:
        """Update age group."""
        self.age_group = age_group

    def adjust_safety_level(self, safety_level) -> None:
        """Adjust safety level."""
        self.safety_level = safety_level

    def validate(self) -> bool:
        """Validate preferences."""
        # Check for inappropriate interests
        inappropriate = ["violence", "adult_content", "scary"]
        for interest in self.interests:
            if any(bad in interest.lower() for bad in inappropriate):
                raise ValueError(f"Inappropriate interest: {interest}")
        return True

    def to_dict(self) -> dict[str, Any]:
        """Convert to dictionary representation."""
        return {
            "language": self.language,
            "interests": self.interests,
            "favorite_colors": self.favorite_colors,
            "favorite_characters": self.favorite_characters,
            "story_themes": self.story_themes,
            "learning_pace": self.learning_pace,
            "audio_preferences": self.audio_preferences,
            "age_group": self.age_group.value if self.age_group else None,
            "safety_level": self.safety_level,
            "voice_preference": self.voice_preference,
        }

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> "ChildPreferences":
        """Create from dictionary representation."""
        age_group = None
        if data.get("age_group"):
            age_group = AgeGroup(data["age_group"])

        return cls(
            language=data.get("language", "en"),
            interests=data.get("interests", []),
            favorite_colors=data.get("favorite_colors", []),
            favorite_characters=data.get("favorite_characters", []),
            story_themes=data.get("story_themes", []),
            learning_pace=data.get("learning_pace", "medium"),
            audio_preferences=data.get("audio_preferences", {}),
            age_group=age_group,
            safety_level=data.get("safety_level", "moderate"),
            voice_preference=data.get("voice_preference", "child_friendly"),
        )

    def copy(self) -> "ChildPreferences":
        """Create a copy of preferences."""
        return ChildPreferences.from_dict(self.to_dict())

    def merge(self, other: "ChildPreferences") -> "ChildPreferences":
        """Merge with another preferences object."""
        merged_dict = self.to_dict()
        other_dict = other.to_dict()

        # Merge lists
        merged_dict["interests"] = list(
            set(merged_dict["interests"] + other_dict["interests"])
        )
        merged_dict["favorite_colors"] = list(
            set(merged_dict["favorite_colors"] + other_dict["favorite_colors"])
        )
        merged_dict["favorite_characters"] = list(
            set(merged_dict["favorite_characters"] + other_dict["favorite_characters"])
        )
        merged_dict["story_themes"] = list(
            set(merged_dict["story_themes"] + other_dict["story_themes"])
        )

        # Override scalars with other's values if they exist
        for key in ["language", "learning_pace", "age_group"]:
            if other_dict[key]:
                merged_dict[key] = other_dict[key]

        # Merge audio preferences
        merged_dict["audio_preferences"].update(other_dict["audio_preferences"])

        return ChildPreferences.from_dict(merged_dict)

    def __eq__(self, other) -> bool:
        """Check equality."""
        if not isinstance(other, ChildPreferences):
            return False
        return self.to_dict() == other.to_dict()

    def get_content_filters(self) -> dict[str, Any]:
        """Get content filtering rules based on preferences."""
        return {
            "age_appropriate": True,
            "language": self.language,
            "excluded_themes": [],  # Can be extended based on parental controls
            "preferred_themes": self.story_themes,
        }
