"""Defines the ChildProfile entity, representing a child's profile information.

This entity encapsulates a child's unique identifier, name, age, and preferences.
It provides methods for creating new profiles, updating existing ones, and
managing domain events related to profile changes. The `ChildProfile` ensures
data integrity through the use of value objects for name and age.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any
from uuid import UUID, uuid4

from src.domain.events.child_profile_updated import ChildProfileUpdated
from src.domain.events.domain_events import DomainEvent
from src.domain.value_objects import ChildAge, ChildName


@dataclass
class ChildProfile:
    """Represents a child's profile with their personal information and preferences."""

    _child_id: UUID
    _child_name: ChildName
    _child_age: ChildAge
    _preferences: dict[str, Any]
    _uncommitted_events: list[DomainEvent] = field(default_factory=list, repr=False)

    @staticmethod
    def create(
        name: str,
        age: int,
        preferences: dict[str, Any] | None = None,
    ) -> ChildProfile:
        """Factory method to create a new ChildProfile with validated value objects.

        Args:
            name: The name of the child.
            age: The age of the child.
            preferences: Optional dictionary of child preferences.

        Returns:
            A new ChildProfile instance.

        """
        child_name = ChildName(name)
        child_age = ChildAge(age)
        profile = ChildProfile(
            _child_id=uuid4(),
            _child_name=child_name,
            _child_age=child_age,
            _preferences=preferences or {},
        )
        # Optionally, raise a creation event
        # from src.domain.events.child_registered import ChildRegistered
        # profile._record_event(ChildRegistered(child_id=profile.id, ...))
        return profile

    @property
    def child_id(self) -> UUID:
        """Gets the unique identifier of the child."""
        return self._child_id

    @property
    def name(self) -> str:
        """Gets the name of the child."""
        return self._child_name.value

    @property
    def age(self) -> int:
        """Gets the age of the child."""
        return self._child_age.value

    @property
    def preferences(self) -> dict[str, Any]:
        """Gets a copy of the child's preferences."""
        return self._preferences.copy()

    def get_uncommitted_events(self) -> list[DomainEvent]:
        """Returns the list of uncommitted domain events."""
        return self._uncommitted_events

    def clear_uncommitted_events(self) -> None:
        """Clears the list of uncommitted domain events."""
        self._uncommitted_events.clear()

    def _record_event(self, event: DomainEvent) -> None:
        """Adds a domain event to the list of uncommitted events.

        Args:
            event: The domain event to record.

        """
        self._uncommitted_events.append(event)

    def update_profile(
        self,
        name: str | None = None,
        age: int | None = None,
        preferences: dict[str, Any] | None = None,
    ) -> None:
        """Update child profile details, validating inputs against domain rules."""
        if name is not None:
            if not name.strip():
                raise ValueError("Child name cannot be empty.")
            # Validate and update name using ChildName value object
            self._child_name = ChildName(name)
        if age is not None:
            if not (2 <= age <= 12):  # Assuming age range 2-12 for COPPA compliance
                raise ValueError(
                    "Child age must be between 2 and 12 for COPPA compliance.",
                )
            # Validate and update age using ChildAge value object
            self._child_age = ChildAge(age)
        if preferences is not None:
            # Update preferences (assuming ChildPreferences handles internal
            # validation)
            self._preferences = preferences

        # Record event after successful updates
        self._record_event(
            ChildProfileUpdated(
                child_id=self._child_id,
                new_name=self.name,
                new_age=self.age,
                new_preferences=self.preferences,
            ),
        )
