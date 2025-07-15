from abc import ABC, abstractmethod
from typing import Optional, List
from uuid import UUID
from datetime import datetime

from src.domain.entities.child_profile import ChildProfile, ChildPreferences, ChildHealthInfo # Assuming these exist


class IChildProfileRepository(ABC):
    """
    Abstract interface for child profile persistence operations.
    """

    @abstractmethod
    async def get_profile_by_id(self, child_id: UUID) -> Optional[ChildProfile]:
        """
        Retrieves a child profile by its ID.
        """
        pass

    @abstractmethod
    async def save_profile(self, profile: ChildProfile) -> None:
        """
        Saves or updates a child profile.
        """
        pass

    @abstractmethod
    async def delete_profile(self, child_id: UUID) -> bool:
        """
        Deletes a child profile by its ID.
        """
        pass

    @abstractmethod
    async def get_child_age(self, child_id: UUID) -> Optional[int]:
        """
        Retrieves the age of a child by their ID.
        """
        pass 