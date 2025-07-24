from uuid import UUID

from src.domain.entities.child_profile import ChildProfile
from src.domain.repositories.event_store import EventStore
from src.infrastructure.logging_config import get_logger


class EventSourcedChildRepository:
    """Repository for Child aggregate using event sourcing with real database backend."""

    def __init__(self, event_store: EventStore) -> None:
        """Initialize repository with real event store implementation.

        Args:
            event_store: Real EventStore implementation (e.g., EventStoreDB with database)
        """
        self.logger = get_logger(__name__, component="persistence")
        self.event_store = event_store
        self.logger.info(
            "EventSourcedChildRepository initialized with real event store"
        )

    async def save(self, child_profile: ChildProfile) -> None:
        await self.event_store.save_events(
            child_profile.id,
            child_profile.get_uncommitted_events(),
        )

    async def get_by_id(self, aggregate_id: UUID) -> ChildProfile | None:
        events = await self.event_store.load_events(aggregate_id)
        if not events:
            return None
        child_profile = ChildProfile.create_new("", 0, {})
        child_profile.id = aggregate_id
        for event in events:
            child_profile.apply(event)
        return child_profile

    async def get_all(self) -> list[ChildProfile]:
        """Get all child profiles from event store by loading all events at once."""
        try:
            # Assuming event_store has a method to load all events efficiently
            all_events = await self.event_store.load_all_events()

            # Group events by aggregate ID
            events_by_aggregate_id = {}
            for event in all_events:
                if event.aggregate_id not in events_by_aggregate_id:
                    events_by_aggregate_id[event.aggregate_id] = []
                events_by_aggregate_id[event.aggregate_id].append(event)

            child_profiles = []
            for aggregate_id, events in events_by_aggregate_id.items():
                child_profile = ChildProfile.create_new("", 0, {})
                child_profile.id = aggregate_id
                for event in events:
                    child_profile.apply(event)
                child_profiles.append(child_profile)

            self.logger.info(f"Retrieved {len(child_profiles)} child profiles")
            return child_profiles
        except Exception as e:
            self.logger.error(f"Error retrieving all child profiles: {e}")
            return []
