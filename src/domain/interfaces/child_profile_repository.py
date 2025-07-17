from abc import ABC, abstractmethod
from uuid import UUID

from src.domain.entities.child_profile import (  # Assuming these exist
    ChildProfile,
)


class IChildProfileRepository(ABC):
    """Abstract interface for child profile persistence operations."""

    @abstractmethod
    async def get_profile_by_id(self, child_id: UUID) -> ChildProfile | None:
        """Retrieves a child profile by its ID."""

    @abstractmethod
    async def save_profile(self, profile: ChildProfile) -> None:
        """Saves or updates a child profile."""

    @abstractmethod
    async def delete_profile(self, child_id: UUID) -> bool:
        """Deletes a child profile by its ID."""

    @abstractmethod
    async def get_child_age(self, child_id: UUID) -> int | None:
        """Retrieves the age of a child by their ID."""
