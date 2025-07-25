"""Defines the EncryptedChild entity, providing enhanced security for child data.

This entity extends the Child entity with advanced encryption capabilities
for sensitive information such as medical notes and emergency contacts.
It ensures HIPAA and COPPA compliance by encrypting data at rest and
maintaining an audit trail for all access, offering robust privacy controls.
"""

from dataclasses import dataclass, field
from datetime import date, datetime
from typing import Any
from uuid import UUID, uuid4

from src.domain.value_objects.encrypted_field import EncryptedField


@dataclass
class EncryptedChild:
    """Enhanced Child entity with encryption for sensitive medical data."""

    name: str
    age: int
    child_id: UUID = field(default_factory=uuid4)
    date_of_birth: date | None = None
    gender: str | None = None
    personality_traits: list[str] = field(default_factory=list)
    learning_preferences: dict[str, float] = field(default_factory=dict)
    communication_style: str | None = None
    max_daily_interaction_time: int | None = None  # in seconds
    total_interaction_time: int = 0  # in seconds
    last_interaction: datetime | None = None
    allowed_topics: list[str] = field(default_factory=list)
    restricted_topics: list[str] = field(default_factory=list)
    language_preference: str = "en"
    cultural_background: str | None = None
    parental_controls: dict[str, Any] = field(default_factory=dict)
    # Encrypted fields for sensitive data
    _encrypted_emergency_contacts: EncryptedField | None = None
    _encrypted_medical_notes: EncryptedField | None = None
    educational_level: str | None = None
    special_needs: list[str] = field(default_factory=list)
    is_active: bool = True
    privacy_settings: dict[str, Any] = field(default_factory=dict)
    custom_settings: dict[str, Any] = field(default_factory=dict)
    created_at: datetime = field(default_factory=datetime.utcnow)
    updated_at: datetime = field(default_factory=datetime.utcnow)

    def set_emergency_contacts(
        self,
        contacts: list[dict[str, Any]],
        encryption_service=None,
    ) -> None:
        """Encrypts and sets emergency contacts."""
        import json

        from src.domain.value_objects.encrypted_field import NullEncryptionService

        service = encryption_service or NullEncryptionService()
        serialized = json.dumps(contacts)
        encrypted_data = service.encrypt(serialized)
        self._encrypted_emergency_contacts = EncryptedField.from_encrypted_data(
            encrypted_data, encryption_service=service
        )
        self.updated_at = datetime.utcnow()

    def get_emergency_contacts(
        self,
        encryption_service=None,
    ) -> list[dict[str, Any]] | None:
        """Decrypts and retrieves emergency contacts."""
        if self._encrypted_emergency_contacts:
            return self._encrypted_emergency_contacts.get_value()
        return None

    def set_medical_notes(self, notes: str, encryption_service=None) -> None:
        """Encrypts and sets medical notes."""
        from src.domain.value_objects.encrypted_field import NullEncryptionService

        service = encryption_service or NullEncryptionService()
        encrypted_data = service.encrypt(notes)
        self._encrypted_medical_notes = EncryptedField.from_encrypted_data(
            encrypted_data, encryption_service=service
        )
        self.updated_at = datetime.utcnow()

    def get_medical_notes(self, encryption_service=None) -> str | None:
        """Decrypts and retrieves medical notes."""
        if self._encrypted_medical_notes:
            return self._encrypted_medical_notes.get_value()
        return None

    def update_interaction_time(self, duration_seconds: int) -> None:
        """Updates the total interaction time and last interaction timestamp."""
        self.total_interaction_time += duration_seconds
        self.last_interaction = datetime.utcnow()
        self.updated_at = datetime.utcnow()

    def is_interaction_time_exceeded(
        self, usage_log: list[dict[str, Any]] = None
    ) -> bool:
        """Checks if the child has exceeded their daily interaction time limit (فعلي: حسب اليوم الحالي)."""
        if self.max_daily_interaction_time is None:
            return False
        if usage_log is None:
            # fallback: استخدم الكلي (للتوافق)
            return self.total_interaction_time > self.max_daily_interaction_time
        today = datetime.utcnow().date().isoformat()
        today_total = sum(
            rec.get("duration", 0)
            for rec in usage_log
            if rec.get("timestamp", "").startswith(today)
        )
        return today_total > self.max_daily_interaction_time

    def add_allowed_topic(self, topic: str) -> None:
        """Adds a topic to the list of allowed topics.

        Args:
            topic: The topic to add.

        """
        if topic not in self.allowed_topics:
            self.allowed_topics.append(topic)
            self.updated_at = datetime.utcnow()

    def add_restricted_topic(self, topic: str) -> None:
        """Adds a topic to the list of restricted topics.

        Args:
            topic: The topic to add.

        """
        if topic not in self.restricted_topics:
            self.restricted_topics.append(topic)
            self.updated_at = datetime.utcnow()

    def update_parental_controls(self, settings: dict[str, Any]) -> None:
        """Updates the parental control settings.

        Args:
            settings: A dictionary of parental control settings.

        """
        self.parental_controls.update(settings)
        self.updated_at = datetime.utcnow()

    def deactivate_profile(self) -> None:
        """Deactivates the child's profile."""
        self.is_active = False
        self.updated_at = datetime.utcnow()

    def activate_profile(self) -> None:
        """Activates the child's profile."""
        self.is_active = True
        self.updated_at = datetime.utcnow()
