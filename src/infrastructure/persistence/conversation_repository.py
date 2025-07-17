from abc import ABC, abstractmethod

from src.domain.entities.conversation import Conversation


class ConversationRepository(ABC):
    @abstractmethod
    async def add(self, conversation: Conversation) -> None:
        pass

    @abstractmethod
    async def get_by_id(self, conversation_id: str) -> Conversation | None:
        pass

    @abstractmethod
    async def get_by_child_id(self, child_id: str) -> list[Conversation]:
        pass

    @abstractmethod
    async def update(self, conversation: Conversation) -> None:
        pass

    @abstractmethod
    async def delete(self, conversation_id: str) -> None:
        pass
