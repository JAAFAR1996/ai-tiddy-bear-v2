from dataclasses import dataclass
from datetime import datetime, timezone
from uuid import UUID, uuid4
from .domain_events import DomainEvent


@dataclass(frozen=True)
class ChildRegistered(DomainEvent):
    child_id: UUID
    name: str
    age: int
    preferences: dict
    
    @classmethod
    def create(cls, child_id: UUID, name: str, age: int, preferences: dict) -> "ChildRegistered":
        return cls(
            event_id=uuid4(),
            timestamp=datetime.now(timezone.utc),
            child_id=child_id,
            name=name,
            age=age,
            preferences=preferences,
        )
