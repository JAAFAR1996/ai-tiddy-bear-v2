"""PostgreSQL Event Store Implementation for Event Sourcing."""

from datetime import datetime
from typing import Any
from uuid import UUID, uuid4

from sqlalchemy import Column, DateTime, Index, Integer, String, select
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.dialects.postgresql import UUID as PGUUID
from src.infrastructure.persistence.models.base import Base

from src.domain.repositories.event_store import EventStore
from src.infrastructure.logging_config import get_logger
from src.infrastructure.persistence.database_manager import Database

logger = get_logger(__name__, component="persistence")


class EventModel(Base):
    """SQLAlchemy model for storing domain events."""

    __tablename__ = "domain_events"

    # Primary key
    event_id: str = Column(PGUUID(as_uuid=True), primary_key=True, default=uuid4)

    # Event metadata
    aggregate_id: str = Column(PGUUID(as_uuid=True), nullable=False, index=True)
    aggregate_type: str = Column(String(100), nullable=False, index=True)
    event_type: str = Column(String(100), nullable=False, index=True)
    event_version: int = Column(Integer, nullable=False, default=1)

    # Event sequence for ordering
    sequence_number: int = Column(Integer, nullable=False)

    # Event data
    event_data: dict[str, Any] = Column(JSONB, nullable=False)
    event_metadata: dict[str, Any] | None = Column(JSONB, nullable=True)

    # Timestamps
    created_at: datetime = Column(DateTime, nullable=False, default=datetime.utcnow)

    # Indexes for performance
    __table_args__ = (
        Index("idx_aggregate_sequence", "aggregate_id", "sequence_number"),
        Index("idx_event_type_created", "event_type", "created_at"),
        Index("idx_aggregate_type", "aggregate_type", "aggregate_id"),
    )


class PostgresEventStore(EventStore):
    """PostgreSQL implementation of EventStore for production use."""

    def __init__(self, database: Database):
        self.db = database

    async def append_events(
        self,
        aggregate_id: UUID,
        aggregate_type: str,
        event_type: str,
        events: list[dict[str, Any]],
    ) -> None:
        """Append a list of events to the event store."""
        async with self.db.get_session() as session:
            for event_data in events:
                # Simplified: assumes current version is max + 1
                # In a real system, you'd handle concurrency control here
                result = await session.execute(
                    select(EventModel)
                    .filter_by(aggregate_id=aggregate_id)
                    .order_by(EventModel.sequence_number.desc())
                    .limit(1),
                )
                last_event = result.scalar_one_or_none()
                sequence = last_event.sequence_number + 1 if last_event else 1

                event = EventModel(
                    aggregate_id=aggregate_id,
                    aggregate_type=aggregate_type,
                    event_type=event_type,
                    sequence_number=sequence,
                    event_data=event_data,
                )
                session.add(event)
            await session.commit()

    async def get_events(
        self,
        aggregate_id: UUID,
        after_version: int | None = None,
    ) -> list[dict[str, Any]]:
        """Retrieve events for a given aggregate."""
        async with self.db.get_session() as session:
            query = (
                select(EventModel)
                .filter_by(aggregate_id=aggregate_id)
                .order_by(EventModel.sequence_number.asc())
            )
            if after_version is not None:
                query = query.filter(EventModel.sequence_number > after_version)

            result = await session.execute(query)
            events = result.scalars().all()
            return [event.event_data for event in events]
