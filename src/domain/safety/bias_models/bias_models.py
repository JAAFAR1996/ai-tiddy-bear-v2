from dataclasses import dataclass
from typing import List, Any


@dataclass
class ConversationContext:
    child_age: int
    child_gender: str = None
    conversation_history: List[str] = None
    interaction_count: int = 0
    session_duration: float = 0.0
    topics_discussed: List[str] = None