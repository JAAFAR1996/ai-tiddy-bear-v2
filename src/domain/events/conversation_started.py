"""Conversation Started Domain Event."""

from dataclasses import dataclass
from datetime import datetime
from typing import Any

"""Conversation Started Domain Event"""


@dataclass
class ConversationStarted:
    """Domain event for conversation start."""

    conversation_id: str
    child_id: str
    started_at: datetime
    initial_message: str
    metadata: dict[str, Any] = None

    def __init__(
        self,
        conversation_id: str,
        child_id: str,
        initial_message: str,
        metadata: dict[str, Any] | None = None,
    ) -> None:
        self.conversation_id = conversation_id
        self.child_id = child_id
        self.initial_message = initial_message
        self.started_at = datetime.now()
        self.metadata = metadata or {}

    def to_dict(self) -> dict[str, Any]:
        """Convert to dictionary."""
        return {
            "conversation_id": self.conversation_id,
            "child_id": self.child_id,
            "started_at": self.started_at.isoformat(),
            "initial_message": self.initial_message,
            "metadata": self.metadata,
        }
