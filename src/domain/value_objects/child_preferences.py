"""Child Preferences Value Object - Domain Layer
This module provides child preference modeling without external dependencies,
maintaining clean domain architecture.
"""

from dataclasses import dataclass, field
from enum import Enum




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
    audio_preferences: dict[str, any] = field(default_factory=dict)
    age_group: AgeGroup = None
    
    def __post_init__(self):
        """Validate preferences after initialization."""
        # Validate language
        if not self.language:
            self.language = "en"
        
        # Validate learning pace
        valid_paces = ["slow", "medium", "fast", "adaptive"]
        if self.learning_pace not in valid_paces:
            self.learning_pace = "medium"
    
    def to_dict(self) -> dict[str, any]:
        """Convert to dictionary representation."""
        return {
            "language": self.language,
            "interests": self.interests,
            "favorite_colors": self.favorite_colors,
            "favorite_characters": self.favorite_characters,
            "story_themes": self.story_themes,
            "learning_pace": self.learning_pace,
            "audio_preferences": self.audio_preferences,
            "age_group": self.age_group.value if self.age_group else None
        }
    
    @classmethod
    def from_dict(cls, data: dict[str, any]) -> "ChildPreferences":
        """Create from dictionary representation."""
        age_group = None
        if "age_group" in data and data["age_group"]:
            age_group = AgeGroup(data["age_group"])
        
        return cls(
            language=data.get("language", "en"),
            interests=data.get("interests", []),
            favorite_colors=data.get("favorite_colors", []),
            favorite_characters=data.get("favorite_characters", []),
            story_themes=data.get("story_themes", []),
            learning_pace=data.get("learning_pace", "medium"),
            audio_preferences=data.get("audio_preferences", {}),
            age_group=age_group
        )
    
    def get_content_filters(self) -> dict[str, any]:
        """Get content filtering rules based on preferences."""
        return {
            "age_appropriate": True,
            "language": self.language,
            "excluded_themes": [],  # Can be extended based on parental controls
            "preferred_themes": self.story_themes
        }
