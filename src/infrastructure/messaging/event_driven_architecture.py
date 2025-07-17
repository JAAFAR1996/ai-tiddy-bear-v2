import uuid
from dataclasses import dataclass, field
from enum import Enum
from typing import Any
from datetime import datetime

class EventType(Enum):
    DOMAIN = "DOMAIN"
    APPLICATION = "APPLICATION"
    INTEGRATION = "INTEGRATION"


@dataclass
class EventMetadata:
    event_id: str = field(default_factory=lambda: str(uuid.uuid4()))
    timestamp: str = field(default_factory=lambda: str(datetime.now()))
    event_type: EventType | None = None
    user_id: str | None = None


@dataclass
class Event:
    data: dict[str, Any]
    metadata: EventMetadata


@dataclass
class Command:
    data: dict[str, Any]
    command_id: str = field(default_factory=lambda: str(uuid.uuid4()))
    user_id: str | None = None


@dataclass
class Query:
    parameters: dict[str, Any]
    query_id: str = field(default_factory=lambda: str(uuid.uuid4()))
    user_id: str | None = None


class InMemoryCommandBus:
    def __init__(self) -> None:
        self.handlers = {}

    async def register_handler(self, command_type, handler):
        self.handlers[command_type] = handler

    async def send(self, command):
        handler = self.handlers.get(type(command))
        if handler:
            return await handler.handle(command)
        raise ValueError(
            f"No handler registered for command type {type(command)}"
        )


class InMemoryQueryBus:
    def __init__(self) -> None:
        self.handlers = {}
        self.cache = {}

    async def register_handler(self, query_type, handler):
        self.handlers[query_type] = handler

    async def ask(self, query):
        # Simplified caching for demonstration
        query_key = f"{type(query).__name__}-{hash(frozenset(query.parameters.items()))}"
        if query_key in self.cache:
            return self.cache[query_key]

        handler = self.handlers.get(type(query))
        if handler:
            result = await handler.handle(query)
            self.cache[query_key] = result
            return result
        raise ValueError(f"No handler registered for query type {type(query)}")


def create_event(
    event_type: EventType,
    data: dict[str, Any],
    user_id: str | None = None,
) -> Event:
    return Event(
        data=data,
        metadata=EventMetadata(event_type=event_type, user_id=user_id),
    )


def create_command(
    data: dict[str, Any], user_id: str | None = None
) -> Command:
    return Command(data=data, user_id=user_id)


def create_query(
    parameters: dict[str, Any], user_id: str | None = None
) -> Query:
    return Query(parameters=parameters, user_id=user_id)
