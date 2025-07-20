from dataclasses import dataclass


@dataclass(slots=True, frozen=True)
class NotificationConfig:
    """Configuration for notification service settings."""

    default_max_attempts: int = 1
    urgent_max_attempts: int = 3
    history_retention_days: int = 30
