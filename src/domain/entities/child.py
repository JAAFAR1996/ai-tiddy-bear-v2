"""Defines the Child entity, representing a child user in the AI Teddy Bear system.

This core domain entity encapsulates comprehensive child information, including
personal details, preferences, safety features, interaction limits, and parental
controls. It is designed with COPPA compliance in mind, ensuring that all data
related to children is handled securely and appropriately.
"""

from dataclasses import dataclass, field
from datetime import UTC, date, datetime
from typing import Any
from uuid import UUID, uuid4


@dataclass
class Child:
    """Child entity representing a child user in the AI Teddy Bear system.

    This entity maintains comprehensive child information with COPPA compliance,
    including safety features, interaction limits, and parental controls.

    Attributes:
        child_id: Unique identifier for the child.
        name: Child's name for personalized interactions.
        age: Child's age (2-12 years for COPPA compliance).
        date_of_birth: Optional birth date for age verification.
        gender: Optional gender identification.
        personality_traits: List of personality characteristics.
        learning_preferences: Dictionary of learning style preferences.
        communication_style: Preferred communication approach.
        max_daily_interaction_time: Daily interaction limit in seconds.
        total_interaction_time: Total accumulated interaction time.
        last_interaction: Timestamp of last interaction.
        allowed_topics: List of topics the child is allowed to discuss.
        restricted_topics: List of topics that are restricted for this child.
        language_preference: Preferred language for interactions.
        cultural_background: Cultural context for appropriate responses.
        parental_controls: Dictionary of parental control settings.
        emergency_contacts: List of emergency contact information.
        medical_notes: Optional medical information for safety.
        educational_level: Child's educational level.
        special_needs: List of special needs or accommodations.
        is_active: Whether the child profile is currently active.
        privacy_settings: Privacy configuration settings.
        custom_settings: Additional custom configuration settings.

    """

    child_id: UUID
    name: str
    age: int
    date_of_birth: date | None = None
    gender: str | None = None
    personality_traits: list[str] = field(default_factory=list)
    learning_preferences: dict[str, Any] = field(default_factory=dict)
    communication_style: str | None = None
    max_daily_interaction_time: int = 3600  # Default to 1 hour
    total_interaction_time: int = 0
    last_interaction: datetime | None = None
    allowed_topics: list[str] = field(default_factory=list)
    restricted_topics: list[str] = field(default_factory=list)
    language_preference: str = "en-US"
    cultural_background: str | None = None
    parental_controls: dict[str, Any] = field(default_factory=dict)
    emergency_contacts: list[dict[str, Any]] = field(default_factory=list)
    medical_notes: str | None = None
    educational_level: str | None = None
    special_needs: list[str] = field(default_factory=list)
    is_active: bool = True
    privacy_settings: dict[str, Any] = field(default_factory=dict)
    custom_settings: dict[str, Any] = field(default_factory=dict)

    @classmethod
    def create_new(
        cls,
        name: str,
        age: int,
        date_of_birth: date | None = None,
        gender: str | None = None,
    ) -> "Child":
        """Factory method to create a new Child instance.

        Args:
            name: The child's name.
            age: The child's age.
            date_of_birth: Optional date of birth.
            gender: Optional gender.

        Returns:
            A new Child instance.

        """
        return cls(
            child_id=uuid4(),
            name=name,
            age=age,
            date_of_birth=date_of_birth,
            gender=gender,
        )

    def update_interaction_time(self, duration_seconds: int) -> None:
        """Updates the total interaction time and last interaction timestamp.

        Args:
            duration_seconds: The duration of the latest interaction in seconds.

        """
        self.total_interaction_time += duration_seconds
        self.last_interaction = datetime.now(UTC)

    daily_interaction_log: dict[date, int] = field(default_factory=dict)

    def is_interaction_time_exceeded(self) -> bool:
        """Checks if the child has exceeded their daily interaction time limit (production logic).

        Returns:
            True if the daily limit is exceeded, False otherwise.
        """
        from datetime import date as dt_date

        today = dt_date.today()
        today_seconds = self.daily_interaction_log.get(today, 0)
        if today_seconds > self.max_daily_interaction_time:
            return True
        return False

    def add_allowed_topic(self, topic: str) -> None:
        """Adds a topic to the list of allowed topics.

        Args:
            topic: The topic to add.

        """
        if topic not in self.allowed_topics:
            self.allowed_topics.append(topic)

    def add_restricted_topic(self, topic: str) -> None:
        """Adds a topic to the list of restricted topics.

        Args:
            topic: The topic to add.

        """
        if topic not in self.restricted_topics:
            self.restricted_topics.append(topic)

    def update_parental_controls(self, settings: dict[str, Any]) -> None:
        """Updates the parental control settings.

        Args:
            settings: A dictionary of parental control settings.

        """
        self.parental_controls.update(settings)

    def deactivate_profile(self) -> None:
        """Deactivates the child's profile."""
        self.is_active = False

    def activate_profile(self) -> None:
        """Activates the child's profile."""
        self.is_active = True
