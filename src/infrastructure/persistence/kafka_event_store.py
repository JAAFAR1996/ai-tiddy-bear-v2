from datetime import datetime
from typing import Any
from uuid import UUID, uuid4

import msgpack
from aiokafka import AIOKafkaConsumer, AIOKafkaProducer
from aiokafka.errors import KafkaError

from src.domain.repositories.event_store import EventStore
from src.infrastructure.config.settings import Settings
from src.infrastructure.logging_config import get_logger

"""Kafka Event Store Implementation for Event Sourcing."""

logger = get_logger(__name__, component="persistence")


class KafkaEventStore(EventStore):
    """Kafka implementation of EventStore for high-throughput event streaming."""

    def __init__(self, settings: Settings) -> None:
        """Initialize Kafka event store.

        Args:
            settings: Application settings with Kafka configuration

        """
        self.bootstrap_servers = settings.kafka.KAFKA_BOOTSTRAP_SERVERS
        self.topic_prefix = "ai-teddy-events"
        self.producer: AIOKafkaProducer | None = None
        self.consumer: AIOKafkaConsumer | None = None
        self._initialized = False

    async def initialize(self) -> None:
        """Initialize Kafka producer and consumer."""
        if self._initialized:
            return

        try:
            # Initialize producer for writing events
            self.producer = AIOKafkaProducer(
                bootstrap_servers=self.bootstrap_servers,
                value_serializer=lambda v: msgpack.packb(v, use_bin_type=True),
                key_serializer=lambda k: k.encode("utf-8") if k else None,
                compression_type="lz4",
                acks="all",  # Wait for all replicas
                retries=5,
                max_batch_size=32768,  # 32KB batches
                linger_ms=10,  # Wait up to 10ms for batching
            )
            await self.producer.start()

            # Initialize consumer for reading events
            self.consumer = AIOKafkaConsumer(
                bootstrap_servers=self.bootstrap_servers,
                value_deserializer=lambda v: msgpack.unpackb(v, raw=False),
                key_deserializer=lambda k: k.decode("utf-8") if k else None,
                auto_offset_reset="earliest",
                enable_auto_commit=False,
                group_id=None,  # No consumer group for event sourcing
                session_timeout_ms=30000,
                max_poll_records=1000,
            )
            await self.consumer.start()

            self._initialized = True
            logger.info("Kafka event store initialized successfully")
        except Exception as e:
            logger.error(f"Failed to initialize Kafka event store: {e}")
            raise

    async def close(self) -> None:
        """Close Kafka connections."""
        if self.producer:
            await self.producer.stop()
        if self.consumer:
            await self.consumer.stop()
        self._initialized = False

    async def save_events(self, aggregate_id: UUID, events: list[Any]) -> None:
        """Save events to Kafka topic.

        Args:
            aggregate_id: UUID of the aggregate
            events: List of domain events to persist

        """
        if not self._initialized:
            await self.initialize()

        if not events:
            return

        topic = self._get_topic_name(aggregate_id)
        try:
            # Send events to Kafka
            futures = []
            for event in events:
                # Prepare event data
                event_data = {
                    "aggregate_id": str(aggregate_id),
                    "event_id": str(uuid4()),
                    "event_type": event.__class__.__name__,
                    "event_version": getattr(event, "__version__", 1),
                    "timestamp": datetime.utcnow().isoformat(),
                    "data": self._serialize_event(event),
                    "metadata": {
                        "user_id": getattr(event, "user_id", None),
                        "correlation_id": getattr(
                            event,
                            "correlation_id",
                            str(uuid4()),
                        ),
                        "causation_id": getattr(
                            event, "causation_id", str(uuid4())
                        ),
                    },
                }

                # Send to Kafka
                future = await self.producer.send(
                    topic=topic,
                    key=str(aggregate_id),
                    value=event_data,
                )
                futures.append(future)

            # Wait for all events to be sent
            for future in futures:
                await future

            logger.info(
                f"Saved {len(events)} events for aggregate {aggregate_id} to Kafka",
            )
        except KafkaError as e:
            logger.error(
                f"Kafka error while saving events for aggregate {aggregate_id}: {e}",
            )
            raise
        except Exception as e:
            logger.error(
                f"Failed to save events for aggregate {aggregate_id}: {e}"
            )
            raise

    async def load_events(self, aggregate_id: UUID) -> list[Any]:
        """Load all events for an aggregate from Kafka.

        Args:
            aggregate_id: UUID of the aggregate
        Returns:
            List of domain events in chronological order

        """
        if not self._initialized:
            await self.initialize()

        topic = self._get_topic_name(aggregate_id)
        try:
            # Subscribe to the specific topic
            self.consumer.subscribe([topic])
            events = []

            # Seek to beginning
            await self.consumer.seek_to_beginning()

            # Read all messages for this aggregate
            async for msg in self.consumer:
                if msg.key == str(aggregate_id):
                    event_data = msg.value
                    # Deserialize event
                    event = self._deserialize_event(
                        event_data["event_type"],
                        event_data["data"],
                        event_data.get("metadata"),
                    )
                    if event:
                        events.append(event)

                # Check if we've reached the end
                partitions = self.consumer.assignment()
                for partition in partitions:
                    position = await self.consumer.position(partition)
                    end_offset = self.consumer.highwater(partition)
                    if position >= end_offset - 1:
                        break

            # Unsubscribe after reading
            self.consumer.unsubscribe()

            logger.debug(
                f"Loaded {len(events)} events for aggregate {aggregate_id} from Kafka",
            )
            return events
        except Exception as e:
            logger.error(
                f"Failed to load events for aggregate {aggregate_id}: {e}"
            )
            raise

    async def load_events_from_offset(
        self,
        aggregate_id: UUID,
        offset: int,
    ) -> list[Any]:
        """Load events from a specific offset.

        Args:
            aggregate_id: UUID of the aggregate
            offset: Kafka offset to start from
        Returns:
            List of domain events from the given offset

        """
        if not self._initialized:
            await self.initialize()

        topic = self._get_topic_name(aggregate_id)
        try:
            self.consumer.subscribe([topic])

            # Seek to specific offset
            partitions = self.consumer.assignment()
            for partition in partitions:
                self.consumer.seek(partition, offset)

            events = []
            async for msg in self.consumer:
                if msg.key == str(aggregate_id):
                    event_data = msg.value
                    event = self._deserialize_event(
                        event_data["event_type"],
                        event_data["data"],
                        event_data.get("metadata"),
                    )
                    if event:
                        events.append(event)

                # Check if we've reached the end
                for partition in partitions:
                    position = await self.consumer.position(partition)
                    end_offset = self.consumer.highwater(partition)
                    if position >= end_offset - 1:
                        break

            self.consumer.unsubscribe()
            return events
        except Exception as e:
            logger.error(
                f"Failed to load events from offset for aggregate {aggregate_id}: {e}",
            )
            raise

    def _get_topic_name(self, aggregate_id: UUID) -> str:
        """Get Kafka topic name for an aggregate.

        Args:
            aggregate_id: UUID of the aggregate
        Returns:
            Kafka topic name

        """
        # Use a partitioning strategy for topic assignment
        # This example uses a simple hash-based partitioning
        partition_id = hash(str(aggregate_id)) % 10
        return f"{self.topic_prefix}-{partition_id}"

    def _serialize_event(self, event: Any) -> dict[str, Any]:
        """Serialize domain event to dictionary.

        Args:
            event: Domain event instance
        Returns:
            Serialized event data

        """
        event_data = {}
        for attr in dir(event):
            if not attr.startswith("_") and not callable(getattr(event, attr)):
                value = getattr(event, attr)
                # Handle special types
                if isinstance(value, UUID):
                    value = str(value)
                elif isinstance(value, datetime):
                    value = value.isoformat()
                elif hasattr(value, "__dict__"):
                    value = value.__dict__
                event_data[attr] = value
        return event_data

    def _deserialize_event(
        self,
        event_type: str,
        event_data: dict[str, Any],
        metadata: dict[str, Any] | None,
    ) -> Any | None:
        """Deserialize event data back to domain event.

        Args:
            event_type: Name of the event class
            event_data: Serialized event data
            metadata: Event metadata
        Returns:
            Domain event instance or None if deserialization fails

        """
        try:
            # Dynamic import based on event type
            if event_type == "ChildRegistered":
                from src.domain.events.child_registered import ChildRegistered

                return ChildRegistered(**event_data)
            if event_type == "ChildProfileUpdated":
                from src.domain.events.child_profile_updated import (
                    ChildProfileUpdated,
                )

                return ChildProfileUpdated(**event_data)
            logger.warning(f"Unknown event type: {event_type}")
            return None
        except Exception as e:
            logger.error(f"Failed to deserialize event {event_type}: {e}")
            return None
