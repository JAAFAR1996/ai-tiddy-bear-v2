from abc import ABC, abstractmethod
from typing import Optional, List
from uuid import UUID

from src.domain.entities.child_profile import ChildProfile  # Assuming ChildProfile is relevant for accessibility
from src.domain.value_objects.accessibility import AccessibilityProfile, SpecialNeedType


class IAccessibilityProfileRepository(ABC):
    """
    Abstract interface for accessibility profile persistence operations.
    """

    @abstractmethod
    async def get_profile_by_child_id(self, child_id: UUID) -> Optional[AccessibilityProfile]:
        """
        Retrieves an accessibility profile for a given child ID.
        """
        pass

    @abstractmethod
    async def save_profile(self, profile: AccessibilityProfile) -> None:
        """
        Saves or updates an accessibility profile.
        """
        pass

    @abstractmethod
    async def delete_profile(self, child_id: UUID) -> bool:
        """
        Deletes an accessibility profile by child ID.
        """
        pass

    @abstractmethod
    async def get_all_profiles(self) -> List[AccessibilityProfile]:
        """
        Retrieves all accessibility profiles.
        """
        pass 