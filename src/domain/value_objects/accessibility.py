from dataclasses import dataclass, field
from enum import Enum
from uuid import UUID


class SpecialNeedType(Enum):
    """Enumeration for different types of special needs a child might have."""

    VISUAL_IMPAIRMENT = "visual_impairment"
    HEARING_IMPAIRMENT = "hearing_impairment"
    SPEECH_IMPAIRMENT = "speech_impairment"
    COGNITIVE_DELAY = "cognitive_delay"
    MOTOR_IMPAIRMENT = "motor_impairment"
    SENSORY_SENSITIVITY = "sensory_sensitivity"
    OTHER = "other"


@dataclass(slots=True)
class AccessibilityProfile:
    """Represents a child's accessibility profile and special needs settings.

    Attributes:
        child_id (UUID): The unique identifier of the child.
        special_needs (List[SpecialNeedType]): A list of special needs types applicable to the child.
        preferred_interaction_mode (str): E.g., "voice", "text", "haptic".
        voice_speed_adjustment (float): Multiplier for voice speed (e.g., 0.8 for slower, 1.2 for faster).
        volume_level (float): Preferred volume level.
        subtitles_enabled (bool): Whether subtitles are preferred/enabled.
        additional_settings (dict): Any other custom accessibility settings.

    """

    child_id: UUID
    special_needs: list[SpecialNeedType] = field(default_factory=list)
    preferred_interaction_mode: str = "voice"
    voice_speed_adjustment: float = 1.0
    volume_level: float = 0.8
    subtitles_enabled: bool = False
    additional_settings: dict = field(default_factory=dict)
