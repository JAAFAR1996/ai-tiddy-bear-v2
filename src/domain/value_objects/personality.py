from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from typing import Any
from uuid import UUID


class PersonalityType(Enum):
    """Enumeration for different child personality types."""

    CURIOUS = "curious"
    CREATIVE = "creative"
    ANALYTICAL = "analytical"
    EMPATHETIC = "empathetic"
    ENERGETIC = "energetic"
    CALM = "calm"
    OTHER = "other"


@dataclass(slots=True)
class ChildPersonality:
    """Represents a child's inferred personality profile.

    Attributes:
        child_id (UUID): The unique identifier of the child.
        personality_type (PersonalityType): The primary personality type inferred for the child.
        traits (Dict[str, float]): A dictionary of personality traits and their scores (e.g., {"openness": 0.7}).
        learning_style (List[str]): Preferred learning styles (e.g., ["visual", "auditory"]).
        interests (List[str]): Key interests of the child.
        last_updated (datetime): Timestamp of the last update to the personality profile.
        metadata (Dict[str, Any]): Additional metadata or raw analysis results.

    """

    child_id: UUID
    personality_type: PersonalityType = PersonalityType.OTHER
    traits: dict[str, float] = field(default_factory=dict)
    learning_style: list[str] = field(default_factory=list)
    interests: list[str] = field(default_factory=list)
    last_updated: datetime = field(default_factory=datetime.now)
    metadata: dict[str, Any] = field(default_factory=dict)
