from dataclasses import dataclass


@dataclass
class ConversationContext:
    child_age: int
    child_gender: str = None
    conversation_history: list[str] = None
    interaction_count: int = 0
    session_duration: float = 0.0
    topics_discussed: list[str] = None
