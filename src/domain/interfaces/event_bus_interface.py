"""Event Bus Interface for Domain Layer
This interface defines event publishing without infrastructure dependencies.
"""

from abc import ABC, abstractmethod

from src.domain.events.base_event import DomainEvent


class EventBusInterface(ABC):
    """Interface for event bus implementations."""

    @abstractmethod
    async def publish(self, event: DomainEvent) -> None:
        """Publish domain event."""

    @abstractmethod
    async def subscribe(self, event_type: str, handler) -> None:
        """Subscribe to domain events."""
