"""Dependency injection configuration for the application."""

from typing import TYPE_CHECKING, Any

if TYPE_CHECKING:
    from src.infrastructure.persistence.child_repository import ChildRepository


from fastapi import Depends


from src.domain.repositories.event_store import EventStore, InMemoryEventStore
from src.infrastructure.repositories.event_sourced_child_repository import (
    EventSourcedChildRepository,
)


def get_event_store() -> EventStore:
    # Production: must use a real event store (e.g., database-backed)
    from src.infrastructure.persistence.event_store_db import EventStoreDB
    return EventStoreDB()


def get_child_repository(
    event_store: EventStore = Depends(get_event_store),
) -> "ChildRepository":
    return EventSourcedChildRepository(event_store)


# Service getters
def get_ai_orchestration_service():
    """Get AI orchestration service."""
    from .di.container import container
    return container.resolve("ai_orchestration_service")


def get_audio_processing_service():
    """Get audio processing service."""
    from .di.container import container
    return container.resolve("audio_processing_service")
