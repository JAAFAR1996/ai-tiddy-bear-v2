from abc import ABC, abstractmethod

from src.application.services.session_manager import (  # Assuming SessionData is in session_manager.py
    SessionData,
)


class ISessionRepository(ABC):
    """Abstract interface for session persistence operations."""

    @abstractmethod
    async def get(self, session_id: str) -> SessionData | None:
        """Retrieves a session by its ID."""

    @abstractmethod
    async def save(self, session_data: SessionData, timeout_minutes: int) -> None:
        """Saves or updates session data, with an associated timeout."""

    @abstractmethod
    async def delete(self, session_id: str) -> bool:
        """Deletes a session by its ID."""

    @abstractmethod
    async def delete_expired(self, timeout_minutes: int) -> None:
        """Deletes all expired sessions."""
