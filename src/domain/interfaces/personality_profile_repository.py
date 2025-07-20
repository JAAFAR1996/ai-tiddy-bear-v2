from abc import ABC, abstractmethod
from uuid import UUID

from src.domain.value_objects.personality import (  # Assuming ChildPersonality is in personality.py
    ChildPersonality,
)


class IPersonalityProfileRepository(ABC):
    """Abstract interface for personality profile persistence operations."""

    @abstractmethod
    async def get_profile_by_child_id(self, child_id: UUID) -> ChildPersonality | None:
        """Retrieves a personality profile for a given child ID."""

    @abstractmethod
    async def save_profile(self, profile: ChildPersonality) -> None:
        """Saves or updates a personality profile."""

    @abstractmethod
    async def delete_profile(self, child_id: UUID) -> bool:
        """Deletes a personality profile by child ID."""

    @abstractmethod
    async def get_all_profiles(self) -> list[ChildPersonality]:
        """Retrieves all personality profiles."""
