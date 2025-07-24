"""Event Store Database Implementation using real PostgreSQL database."""

import uuid
from typing import Any, Dict, List, Optional
from uuid import UUID

from sqlalchemy import text
from sqlalchemy.exc import IntegrityError, SQLAlchemyError

from src.domain.repositories.event_store import EventStore
from src.infrastructure.logging_config import get_logger
from src.infrastructure.persistence.database_manager import Database

logger = get_logger(__name__, component="persistence")


class ConcurrencyError(Exception):
    """Raised when optimistic concurrency control fails."""


class DatabaseError(Exception):
    """Raised when database operations fail."""


class EventStoreDB(EventStore):
    """Real database implementation of EventStore for production use.

    This implementation uses PostgreSQL with proper transaction handling,
    concurrency control, and error handling for production environments.

    PRODUCTION REQUIREMENT: Uses real database persistence, NO in-memory storage.
    """

    def __init__(self, database: Database):
        """Initialize EventStoreDB with real database connection.

        Args:
            database: Real Database instance with PostgreSQL connection
        """
        self.db = database
        self.logger = logger

        # PRODUCTION REQUIREMENT: Real database persistence only
        # NO in-memory storage allowed

        self.logger.info(
            "EventStoreDB initialized with real PostgreSQL database connection"
        )

    async def _get_current_version(self, session, aggregate_id: UUID) -> int:
        """Get the current version of an aggregate from database."""
        try:
            result = await session.execute(
                text(
                    """
                SELECT COALESCE(MAX(sequence_number), 0) as max_version
                FROM domain_events
                WHERE aggregate_id = :aggregate_id
                """
                ),
                {"aggregate_id": str(aggregate_id)},
            )
            row = result.fetchone()
            return row[0] if row else 0
        except SQLAlchemyError as e:
            self.logger.error(
                f"Failed to get current version for aggregate {aggregate_id}: {str(e)}"
            )
            raise DatabaseError(f"Failed to get version: {str(e)}") from e

    async def save_events(
        self,
        aggregate_id: UUID,
        events: List[Any],
        expected_version: Optional[int] = None,
    ) -> None:
        """Save events to PostgreSQL database with transaction safety.

        Args:
            aggregate_id: The ID of the aggregate
            events: List of domain events to save
            expected_version: Expected version for optimistic concurrency control

        Raises:
            ConcurrencyError: If expected version doesn't match current version
            DatabaseError: If database operation fails
        """
        if not events:
            return

        try:
            async with self.db.get_session() as session:
                # Get current version from database
                current_version = await self._get_current_version(session, aggregate_id)

                # Optimistic concurrency control
                if expected_version is not None and current_version != expected_version:
                    raise ConcurrencyError(
                        f"Concurrency conflict for aggregate {aggregate_id}. "
                        f"Expected version {expected_version}, but current version is {current_version}"
                    )

                # Save events to database with proper sequencing
                for i, event in enumerate(events):
                    # Handle both dict and domain event objects
                    if isinstance(event, dict):
                        event_data = event
                        event_type = event.get("event_type", "DomainEvent")
                        aggregate_type = event.get("aggregate_type", "ChildProfile")
                    else:
                        event_data = (
                            event.to_dict()
                            if hasattr(event, "to_dict")
                            else event.__dict__
                        )
                        event_type = event.__class__.__name__
                        aggregate_type = (
                            event.__class__.__module__.split(".")[-2]
                            if "." in event.__class__.__module__
                            else "ChildProfile"
                        )

                    event_record = {
                        "event_id": str(uuid.uuid4()),
                        "aggregate_id": str(aggregate_id),
                        "aggregate_type": aggregate_type,
                        "event_type": event_type,
                        "event_version": current_version + i + 1,
                        "sequence_number": current_version + i + 1,
                        "event_data": event_data,
                        "event_metadata": {
                            "timestamp": getattr(event, "timestamp", None),
                            "correlation_id": getattr(event, "correlation_id", None),
                            "causation_id": getattr(event, "causation_id", None),
                        },
                    }

                    # Insert into database using parameterized query
                    await session.execute(
                        text(
                            """
                        INSERT INTO domain_events (
                            event_id, aggregate_id, aggregate_type, event_type,
                            event_version, sequence_number, event_data, event_metadata, created_at
                        ) VALUES (
                            :event_id::uuid, :aggregate_id::uuid, :aggregate_type, :event_type,
                            :event_version, :sequence_number, :event_data::jsonb, :event_metadata::jsonb, NOW()
                        )
                        """
                        ),
                        event_record,
                    )

                await session.commit()
                self.logger.info(
                    f"Saved {len(events)} events for aggregate {aggregate_id}"
                )

        except IntegrityError as e:
            self.logger.error(
                f"Database integrity error saving events for aggregate {aggregate_id}: {str(e)}"
            )
            raise DatabaseError(f"Event store integrity violation: {str(e)}") from e
        except SQLAlchemyError as e:
            self.logger.error(
                f"Database error saving events for aggregate {aggregate_id}: {str(e)}"
            )
            raise DatabaseError(f"Event store database error: {str(e)}") from e
        except Exception as e:
            self.logger.error(
                f"Unexpected error saving events for aggregate {aggregate_id}: {str(e)}"
            )
            raise DatabaseError(f"Event store save failed: {str(e)}") from e

    async def load_events(self, aggregate_id: UUID) -> List[Dict[str, Any]]:
        """Load events for an aggregate from PostgreSQL database.

        Args:
            aggregate_id: The ID of the aggregate

        Returns:
            List of event dictionaries in sequence order

        Raises:
            DatabaseError: If database operation fails
        """
        try:
            async with self.db.get_session() as session:
                result = await session.execute(
                    text(
                        """
                    SELECT event_data, event_type, sequence_number, created_at
                    FROM domain_events
                    WHERE aggregate_id = :aggregate_id
                    ORDER BY sequence_number ASC
                    """
                    ),
                    {"aggregate_id": str(aggregate_id)},
                )

                events = []
                for row in result.fetchall():
                    events.append(
                        {
                            "data": row[0],  # event_data JSONB
                            "event_type": row[1],
                            "version": row[2],  # sequence_number
                            "timestamp": row[3].isoformat() if row[3] else None,
                        }
                    )

                self.logger.info(
                    f"Loaded {len(events)} events for aggregate {aggregate_id}"
                )
                return events

        except SQLAlchemyError as e:
            self.logger.error(
                f"Database error loading events for aggregate {aggregate_id}: {str(e)}"
            )
            raise DatabaseError(f"Event store load failed: {str(e)}") from e
        except Exception as e:
            self.logger.error(
                f"Unexpected error loading events for aggregate {aggregate_id}: {str(e)}"
            )
            raise DatabaseError(f"Event store load failed: {str(e)}") from e

    async def get_events(
        self,
        aggregate_id: UUID,
        after_version: Optional[int] = None,
    ) -> List[Dict[str, Any]]:
        """Get events from the database store with version filtering.

        Args:
            aggregate_id: The ID of the aggregate
            after_version: Only return events after this version number

        Returns:
            List of event dictionaries
        """
        try:
            async with self.db.get_session() as session:
                query = """
                SELECT event_data, event_type, sequence_number, created_at
                FROM domain_events
                WHERE aggregate_id = :aggregate_id
                """
                params = {"aggregate_id": str(aggregate_id)}

                if after_version is not None:
                    query += " AND sequence_number > :after_version"
                    params["after_version"] = after_version

                query += " ORDER BY sequence_number ASC"

                result = await session.execute(text(query), params)

                events = []
                for row in result.fetchall():
                    events.append(
                        {
                            "aggregate_id": str(aggregate_id),
                            "event_type": row[1],
                            "version": row[2],
                            "data": row[0],
                            "timestamp": row[3].isoformat() if row[3] else None,
                        }
                    )

                self.logger.info(
                    f"Retrieved {len(events)} events for aggregate {aggregate_id}"
                )
                return events

        except SQLAlchemyError as e:
            self.logger.error(
                f"Database error getting events for aggregate {aggregate_id}: {str(e)}"
            )
            raise DatabaseError(f"Event store get failed: {str(e)}") from e

    async def append_events(
        self,
        aggregate_id: UUID,
        aggregate_type: str,
        event_type: str,
        events: List[Dict[str, Any]],
    ) -> None:
        """Append events to the database-backed store.

        Args:
            aggregate_id: The ID of the aggregate
            aggregate_type: Type of the aggregate
            event_type: Type of the events
            events: List of event data dictionaries
        """
        # Convert to format expected by save_events
        formatted_events = []
        for event in events:
            if isinstance(event, dict):
                formatted_events.append(event)
            else:
                formatted_events.append({"data": event, "event_type": event_type})

        await self.save_events(aggregate_id, formatted_events)

    async def load_all_events(self) -> List[Dict[str, Any]]:
        """Load all events from all aggregates in the database.

        Returns:
            List of all events with aggregate information

        Raises:
            DatabaseError: If database operation fails
        """
        try:
            async with self.db.get_session() as session:
                result = await session.execute(
                    text(
                        """
                    SELECT aggregate_id, event_data, event_type, sequence_number, created_at
                    FROM domain_events
                    ORDER BY aggregate_id, sequence_number ASC
                    """
                    )
                )

                events = []
                for row in result.fetchall():
                    events.append(
                        {
                            "aggregate_id": UUID(row[0]),
                            "data": row[1],  # event_data JSONB
                            "event_type": row[2],
                            "version": row[3],  # sequence_number
                            "timestamp": row[4].isoformat() if row[4] else None,
                        }
                    )

                self.logger.info(
                    f"Loaded {len(events)} total events from all aggregates"
                )
                return events

        except SQLAlchemyError as e:
            self.logger.error(f"Database error loading all events: {str(e)}")
            raise DatabaseError(f"Event store load all failed: {str(e)}") from e
        except Exception as e:
            self.logger.error(f"Unexpected error loading all events: {str(e)}")
            raise DatabaseError(f"Event store load all failed: {str(e)}") from e
