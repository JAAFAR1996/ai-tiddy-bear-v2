"""Dependency injection configuration for the application."""

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from src.infrastructure.persistence.child_repository import ChildRepository


from src.domain.repositories.event_store import EventStore
from src.infrastructure.repositories.event_sourced_child_repository import (
    EventSourcedChildRepository,
)


def get_event_store() -> EventStore:
    """Get real database-backed event store for production use."""
    from src.infrastructure.persistence.database_manager import Database
    from src.infrastructure.persistence.event_store_db import EventStoreDB

    # Create real database connection
    database = Database()

    # Return real database-backed event store
    return EventStoreDB(database)


def get_child_repository() -> "ChildRepository":
    """Get child repository with resolved dependencies."""
    event_store = get_event_store()
    return EventSourcedChildRepository(event_store)


# Service getters
def get_manage_child_profile_use_case():
    """Get manage child profile use case."""
    from src.application.use_cases.manage_child_profile import ManageChildProfileUseCase
    from src.infrastructure.messaging.kafka_event_bus import KafkaEventBus
    from src.infrastructure.read_models.child_profile_read_model import (
        ChildProfileReadModelStore,
    )

    # Get repository dependency
    child_repository = get_child_repository()

    # Initialize read model store
    read_model_store = ChildProfileReadModelStore()

    # Initialize event bus with default configuration for development
    event_bus = KafkaEventBus(
        bootstrap_servers="localhost:9092", schema_registry_url="http://localhost:8081"
    )

    return ManageChildProfileUseCase(
        child_repository=child_repository,
        child_profile_read_model_store=read_model_store,
        event_bus=event_bus,
    )


def get_generate_dynamic_story_use_case():
    """Get generate dynamic story use case."""
    from src.application.use_cases.generate_dynamic_story import (
        GenerateDynamicStoryUseCase,
    )

    return GenerateDynamicStoryUseCase()


def get_ai_orchestration_service():
    """Get AI orchestration service."""
    from .di.container import container

    return container.resolve("ai_orchestration_service")


def get_audio_processing_service():
    """Get audio processing service."""
    from .di.container import container

    return container.resolve("audio_processing_service")
