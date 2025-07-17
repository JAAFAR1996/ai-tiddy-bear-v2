from abc import ABC, abstractmethod
from typing import Optional, List
from uuid import UUID

from src.domain.value_objects.personality import (
    ChildPersonality,
)  # Assuming ChildPersonality is in personality.py


class IPersonalityProfileRepository(ABC):
    """
    Abstract interface for personality profile persistence operations.
    """

    @abstractmethod
    async def get_profile_by_child_id(
        self, child_id: UUID
    ) -> Optional[ChildPersonality]:
        """
        Retrieves a personality profile for a given child ID.
        """
        pass

    @abstractmethod
    async def save_profile(self, profile: ChildPersonality) -> None:
        """
        Saves or updates a personality profile.
        """
        pass

    @abstractmethod
    async def delete_profile(self, child_id: UUID) -> bool:
        """
        Deletes a personality profile by child ID.
        """
        pass

    @abstractmethod
    async def get_all_profiles(self) -> List[ChildPersonality]:
        """
        Retrieves all personality profiles.
        """
        pass
