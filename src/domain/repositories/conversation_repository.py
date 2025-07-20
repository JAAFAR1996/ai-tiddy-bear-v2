from typing import Protocol
from uuid import UUID

from src.domain.entities.conversation import Conversation


class ConversationRepository(Protocol):
    async def save(self, conversation: Conversation) -> None: ...

    async def get_by_id(self, conversation_id: UUID) -> Conversation | None: ...

    async def find_by_child_id(self, child_id: UUID) -> list[Conversation]: ...

    async def delete(self, conversation_id: UUID) -> None: ...
