from dataclasses import dataclass
from datetime import datetime
from typing import Dict, Any, Optional
from uuid import UUID


@dataclass
class ChildProfileUpdated:
    """Domain event for child profile updates - required for COPPA compliance audit trail."""
    child_id: UUID
    name: Optional[str] = None
    age: Optional[int] = None
    preferences: Optional[Dict[str, Any]] = None
    # Previous values for audit trail
    previous_name: Optional[str] = None
    previous_age: Optional[int] = None
    previous_preferences: Optional[Dict[str, Any]] = None
    # Event metadata
    event_timestamp: datetime = None
    event_id: UUID = None

    def __post_init__(self):
        """Initialize event metadata after creation."""
        if self.event_timestamp is None:
            self.event_timestamp = datetime.utcnow()
        if self.event_id is None:
            from uuid import uuid4
            self.event_id = uuid4()

    @staticmethod
    def create(child_id: UUID, name: Optional[str] = None, age: Optional[int] = None,
              preferences: Optional[Dict[str, Any]] = None,
              previous_name: Optional[str] = None, previous_age: Optional[int] = None,
              previous_preferences: Optional[Dict[str, Any]] = None) -> 'ChildProfileUpdated':
        """Create a new ChildProfileUpdated event with audit trail."""
        return ChildProfileUpdated(
            child_id=child_id,
            name=name,
            age=age,
            preferences=preferences,
            previous_name=previous_name,
            previous_age=previous_age,
            previous_preferences=previous_preferences
        )
