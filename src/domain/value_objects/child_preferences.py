"""Child Preferences Value Object - Domain Layer
This module provides child preference modeling without external dependencies,
maintaining clean domain architecture."""

from dataclasses import dataclass, field
from enum import Enum
from typing import List, Dict, Any, Optional
import re


class AgeGroup(Enum):
    """Age groups for children with corresponding values for safety checks."""
    TODDLER = 3  # 2-4 years
    PRESCHOOL = 5  # 4-6 years
    EARLY_SCHOOL = 7  # 6-8 years
    SCHOOL = 10  # 8-12 years
    TWEEN = 12  # 10-13 years
    TEEN = 15  # 13-18 years


@dataclass
class ChildPreferences:
    """
    Child Preferences Value Object
    Represents a child's preferences for interaction, learning, and communication.
    This is a pure domain value object without external dependencies.
    """
    language: str = "ar"
    favorite_topics: List[str] = field(default_factory=list)
    voice_preference: Optional[str] = "friendly"
    learning_level: int = 1  # 1-5, for adaptive complexity
    vocabulary_size: int = 0  # Estimated vocabulary size
    preferred_learning_style: Optional[str] = None  # e.g., "auditory", "visual"
    interaction_history_summary: Optional[str] = None  # Summary of past interactions
    emotional_tendencies: Dict[str, float] = field(
        default_factory=dict
    )  # e.g., {"happy": 0.7, "sad": 0.1}
    age: int = 8  # Child's age in years
    
    def __post_init__(self) -> None:
        """Validate child preferences after initialization."""
        self._validate_language()
        self._validate_learning_level()
        self._validate_age()
    
    def _validate_language(self) -> None:
        """Validate language preference."""
        if self.language not in ["ar", "en", "fr", "es"]:
            raise ValueError("Unsupported language")
    
    def _validate_learning_level(self) -> None:
        """Validate learning level."""
        if not 1 <= self.learning_level <= 5:
            raise ValueError("Learning level must be between 1 and 5")
    
    def _validate_age(self) -> None:
        """Validate age range."""
        if not 2 <= self.age <= 18:
            raise ValueError("Age must be between 2 and 18 years")
    
    @property
    def age_group(self) -> AgeGroup:
        """Compute age group based on child's age."""
        if self.age <= 4:
            return AgeGroup.TODDLER
        elif self.age <= 6:
            return AgeGroup.PRESCHOOL
        elif self.age <= 8:
            return AgeGroup.EARLY_SCHOOL
        elif self.age <= 12:
            return AgeGroup.SCHOOL
        elif self.age <= 13:
            return AgeGroup.TWEEN
        else:
            return AgeGroup.TEEN