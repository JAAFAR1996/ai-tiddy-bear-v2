from abc import ABC, abstractmethod
from typing import Any
from uuid import UUID


class EventStore(ABC):
    @abstractmethod
    async def save_events(self, aggregate_id: UUID, events: list[Any]) -> None:
        pass

    @abstractmethod
    async def load_events(self, aggregate_id: UUID) -> list[Any]:
        pass


class InMemoryEventStore(EventStore):
    def __init__(self) -> None:
        self.events: dict[UUID, list[Any]] = {}

    async def save_events(self, aggregate_id: UUID, events: list[Any]) -> None:
        if aggregate_id not in self.events:
            self.events[aggregate_id] = []
        self.events[aggregate_id].extend(events)

    async def load_events(self, aggregate_id: UUID) -> list[Any]:
        return self.events.get(aggregate_id, [])
