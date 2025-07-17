from dataclasses import dataclass


@dataclass(slots=True, frozen=True)
class InteractionConfig:
    """Configuration for interaction service settings."""

    max_message_length: int = 500
    min_child_age: int = 3
    max_child_age: int = 12
