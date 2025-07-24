"""Event Store interface and implementation for Event Sourcing pattern."""

from abc import ABC, abstractmethod
from typing import Any, Dict, List
from uuid import UUID


class EventStore(ABC):
    """Abstract base class for event store implementations."""

    @abstractmethod
    async def append_events(
        self,
        aggregate_id: UUID,
        aggregate_type: str,
        event_type: str,
        events: List[Dict[str, Any]],
    ) -> None:
        """Append events to the event store."""

    @abstractmethod
    async def get_events(
        self,
        aggregate_id: UUID,
        after_version: int = None,
    ) -> List[Dict[str, Any]]:
        """Retrieve events for an aggregate."""


class InMemoryEventStore(EventStore):
    """In-memory implementation of EventStore for testing."""

    def __init__(self):
        self._events: Dict[str, List[Dict[str, Any]]] = {}
        self._versions: Dict[str, int] = {}

    async def append_events(
        self,
        aggregate_id: UUID,
        aggregate_type: str,
        event_type: str,
        events: List[Dict[str, Any]],
    ) -> None:
        """Append events to memory store."""
        key = str(aggregate_id)
        if key not in self._events:
            self._events[key] = []
            self._versions[key] = 0

        for event in events:
            self._versions[key] += 1
            event_with_metadata = {
                "aggregate_id": str(aggregate_id),
                "aggregate_type": aggregate_type,
                "event_type": event_type,
                "version": self._versions[key],
                "data": event,
            }
            self._events[key].append(event_with_metadata)

    async def get_events(
        self,
        aggregate_id: UUID,
        after_version: int = None,
    ) -> List[Dict[str, Any]]:
        """Get events from memory store."""
        key = str(aggregate_id)
        events = self._events.get(key, [])

        if after_version is not None:
            return [e for e in events if e.get("version", 0) > after_version]
        return events
