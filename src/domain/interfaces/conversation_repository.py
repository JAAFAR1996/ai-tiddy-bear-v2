from abc import ABC, abstractmethod
from uuid import UUID

from src.domain.entities.conversation import Conversation


class IConversationRepository(ABC):
    """Abstract interface for conversation persistence operations."""

    @abstractmethod
    async def save(self, conversation: Conversation) -> None:
        """Saves or updates a conversation."""

    @abstractmethod
    async def find_by_child_id(self, child_id: UUID) -> list[Conversation]:
        """Retrieves all conversations for a specific child."""

    @abstractmethod
    async def get_by_id(self, conversation_id: UUID) -> Conversation | None:
        """Retrieves a single conversation by its ID."""
