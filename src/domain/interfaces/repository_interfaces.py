"""Repository interfaces for the domain layer.
These interfaces define contracts for data persistence without
creating dependencies on specific database implementations.
"""

from abc import ABC, abstractmethod
from uuid import UUID

from src.domain.entities.user import User

from ..entities.child import Child


class IChildRepository(ABC):
    """Interface for child data persistence."""

    @abstractmethod
    async def create(self, child: Child) -> Child:
        """Create a new child record."""

    @abstractmethod
    async def get_by_id(self, child_id: UUID) -> Child | None:
        """Get a child by ID."""

    @abstractmethod
    async def get_by_parent_id(self, parent_id: UUID) -> list[Child]:
        """Get all children for a parent."""

    @abstractmethod
    async def update(self, child: Child) -> Child:
        """Update an existing child record."""

    @abstractmethod
    async def delete(self, child_id: UUID) -> bool:
        """Delete a child record."""


class IUserRepository(ABC):
    """Interface for user data persistence."""

    @abstractmethod
    async def create(self, user: User) -> User:
        """Create a new user record."""

    @abstractmethod
    async def get_by_id(self, user_id: UUID) -> User | None:
        """Get a user by ID."""

    @abstractmethod
    async def get_by_email(self, email: str) -> User | None:
        """Get a user by email address."""

    @abstractmethod
    async def update(self, user: User) -> User:
        """Update an existing user record."""

    @abstractmethod
    async def delete(self, user_id: UUID) -> bool:
        """Delete a user record."""
