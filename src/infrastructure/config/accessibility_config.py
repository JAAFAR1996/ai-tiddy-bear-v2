from dataclasses import dataclass, field
from typing import Dict, List


@dataclass(slots=True, frozen=True)
class AccessibilityConfig:
    """Configuration for accessibility settings and adaptations.

    Attributes:
        adaptation_rules (Dict[str, List[str]]): A mapping from special need type (string value) to a list of adaptations.
        accessibility_settings_rules (Dict[str, Dict[str, bool]]): A mapping from special need type (string value) to a dictionary of setting overrides.
    """

    adaptation_rules: Dict[str, List[str]] = field(
        default_factory=lambda: {
            "visual_impairment": ["audio_descriptions", "high_contrast", "large_text"],
            "hearing_impairment": ["visual_cues", "subtitles", "sign_language"],
            "motor_difficulties": ["simplified_controls", "voice_activation"],
            "cognitive_delay": ["simplified_language", "slower_pacing"],
            "sensory_sensitivity": ["calm_audio_only", "low_light_mode"],
        }
    )
    accessibility_settings_rules: Dict[str, Dict[str, bool]] = field(
        default_factory=lambda: {
            "hearing_impairment": {"audio_enabled": False},
            "visual_impairment": {"visual_enabled": False},
            "motor_difficulties": {"simplified_ui": True},
            "learning_disabilities": {"simplified_ui": True},
            "cognitive_delay": {"simplified_ui": True},
        }
    )
