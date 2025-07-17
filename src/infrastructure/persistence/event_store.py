"""from datetime import datetime
from typing import List, Dict, Any, Optional
from uuid import uuid4
import asyncio
import json
import logging
from src.domain.events.base_event import DomainEvent
from src.infrastructure.persistence.database import get_database.
"""

"""Real Event Store Implementation for Domain Events
Enterprise-grade event sourcing with proper persistence and replay capabilities
"""

from src.infrastructure.logging_config import get_logger

logger = get_logger(__name__, component="persistence")


class EventStore:
    """Provides event sourcing capabilities with persistent storage."""

    def __init__(self) -> None:
        self.database = get_database()

    async def store_event(self, event: DomainEvent) -> str:
        """Store domain event with persistence and audit trail."""
        try:
            async with self.database.get_session() as session:
                event_id = str(uuid4())

                # Serialize event data
                event_data = {
                    "event_id": event_id,
                    "event_type": event.__class__.__name__,
                    "aggregate_id": str(event.aggregate_id),
                    "aggregate_version": event.version,
                    "event_data": event.to_dict(),
                    "occurred_at": event.occurred_at.isoformat(),
                    "created_at": datetime.utcnow().isoformat(),
                }

                # Store in events table
                query = """
                INSERT INTO domain_events
                (event_id, event_type, aggregate_id, aggregate_version,
                 event_data, occurred_at, created_at)
                VALUES
                (: event_id, : event_type, : aggregate_id, : aggregate_version, : event_data, : occurred_at, : created_at)
                """
                await session.execute(
                    query,
                    {
                        "event_id": event_id,
                        "event_type": event_data["event_type"],
                        "aggregate_id": event_data["aggregate_id"],
                        "aggregate_version": event_data["aggregate_version"],
                        "event_data": json.dumps(event_data["event_data"]),
                        "occurred_at": event_data["occurred_at"],
                        "created_at": event_data["created_at"],
                    },
                )

                logger.info(
                    f"Stored event {event_id} for aggregate {event.aggregate_id}",
                )
                return event_id
        except Exception as e:
            logger.error(f"Failed to store event: {e}")
            raise RuntimeError(f"Event storage failed: {e}") from e

    async def get_events(
        self,
        aggregate_id: str,
        from_version: int = 0,
    ) -> List[DomainEvent]:
        """Load events for event replay and aggregate reconstruction."""
        try:
            async with self.database.get_session() as session:
                query = """
                SELECT event_type, event_data, occurred_at, aggregate_version
                FROM domain_events
                WHERE aggregate_id = : aggregate_id
                AND aggregate_version > : from_version
                ORDER BY aggregate_version ASC
                """
                result = await session.execute(
                    query,
                    {"aggregate_id": aggregate_id, "from_version": from_version},
                )

                events = []
                for row in result.fetchall():
                    # Reconstruct event from stored data
                    event_data = json.loads(row.event_data)

                    # Create event instance (simplified - in production would use event factory)
                    event = DomainEvent(
                        aggregate_id=aggregate_id,
                        version=row.aggregate_version,
                        occurred_at=datetime.fromisoformat(row.occurred_at),
                        data=event_data,
                    )
                    events.append(event)

                logger.info(
                    f"Retrieved {len(events)} events for aggregate {aggregate_id}",
                )
                return events
        except Exception as e:
            logger.error(f"Failed to retrieve events: {e}")
            raise RuntimeError(f"Event retrieval failed: {e}") from e

    async def get_all_events(
        self,
        event_type: Optional[str] = None,
    ) -> List[DomainEvent]:
        """Support for event replay and system rebuilding."""
        try:
            async with self.database.get_session() as session:
                if event_type:
                    query = """
                    SELECT event_id, aggregate_id, aggregate_version, event_type,
                           event_data, occurred_at, created_at, metadata
                    FROM domain_events
                    WHERE event_type = : event_type
                    ORDER BY created_at ASC
                    LIMIT : limit OFFSET : offset
                    """
                    params = {"event_type": event_type, "limit": 1000, "offset": 0}
                else:
                    query = """
                    SELECT event_id, aggregate_id, aggregate_version, event_type,
                           event_data, occurred_at, created_at, metadata
                    FROM domain_events
                    ORDER BY created_at ASC
                    LIMIT : limit OFFSET : offset
                    """
                    params = {"limit": 1000, "offset": 0}

                result = await session.execute(query, params)
                events = []
                for row in result.fetchall():
                    event_data = json.loads(row.event_data)
                    event = DomainEvent(
                        aggregate_id=row.aggregate_id,
                        version=row.aggregate_version,
                        occurred_at=datetime.fromisoformat(row.occurred_at),
                        data=event_data,
                    )
                    events.append(event)

                return events
        except Exception as e:
            logger.error(f"Failed to get all events: {e}")
            raise RuntimeError(f"Event query failed: {e}") from e
