from dataclasses import dataclass
from uuid import UUID

from src.domain.events.domain_events import DomainEvent


@dataclass(frozen=True)
class ConversationUpdatedEvent(DomainEvent):
    conversation_id: UUID
    child_id: UUID
    updated_summary: str
    updated_emotion_analysis: str
    updated_sentiment_score: float
