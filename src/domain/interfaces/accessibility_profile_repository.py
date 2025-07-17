from abc import ABC, abstractmethod
from uuid import UUID

from src.domain.value_objects.accessibility import AccessibilityProfile


class IAccessibilityProfileRepository(ABC):
    """Abstract interface for accessibility profile persistence operations."""

    @abstractmethod
    async def get_profile_by_child_id(
        self,
        child_id: UUID,
    ) -> AccessibilityProfile | None:
        """Retrieves an accessibility profile for a given child ID."""

    @abstractmethod
    async def save_profile(self, profile: AccessibilityProfile) -> None:
        """Saves or updates an accessibility profile."""

    @abstractmethod
    async def delete_profile(self, child_id: UUID) -> bool:
        """Deletes an accessibility profile by child ID."""

    @abstractmethod
    async def get_all_profiles(self) -> list[AccessibilityProfile]:
        """Retrieves all accessibility profiles."""
