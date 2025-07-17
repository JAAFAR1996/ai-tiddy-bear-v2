from dataclasses import dataclass
from datetime import datetime
from uuid import UUID, uuid4

@dataclass(frozen=True)
class DomainEvent:
    event_id: UUID
    timestamp: datetime
    
    def __post_init__(self) -> None:
        # Ensure UUID is a UUID object and datetime is a datetime object
        if isinstance(self.event_id, str):
            super().__setattr__("event_id", UUID(self.event_id))
        if isinstance(self.timestamp, str):
            super().__setattr__("timestamp", datetime.fromisoformat(self.timestamp))
    
    @classmethod
    def new_event(cls) -> 'DomainEvent':
        return cls(event_id=uuid4(), timestamp=datetime.utcnow())