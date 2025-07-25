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
    async def get_all_profiles(
        self, batch_size: int = 100, cursor: int = 0, max_profiles: int | None = None
    ) -> list[ChildPersonality]:
        """Retrieves all personality profiles with efficient pagination support.

        Args:
            batch_size: Number of keys to process per iteration (default: 100)
            cursor: Starting cursor for pagination (default: 0)
            max_profiles: Maximum number of profiles to return (default: None)

        Returns:
            List of ChildPersonality objects
        """
