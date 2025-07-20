from dataclasses import dataclass, field
from datetime import UTC, datetime
from enum import Enum
from typing import Any
from uuid import UUID, uuid4


class NotificationStatus(Enum):
    """Status of a notification."""

    PENDING = "pending"
    SENT = "sent"
    FAILED = "failed"
    DELIVERED = "delivered"
    READ = "read"
    ARCHIVED = "archived"


@dataclass(slots=True)
class NotificationRecord:
    """Represents a single notification record for persistence and tracking."""

    id: UUID = field(default_factory=uuid4)
    recipient: str
    message: str
    notification_type: str
    channel: str
    urgent: bool
    created_at: datetime = field(default_factory=lambda: datetime.now(UTC))
    status: NotificationStatus = NotificationStatus.PENDING
    attempts: int = 0
    max_attempts: int = 3
    last_attempt_at: datetime | None = None
    error_message: str | None = None
    metadata: dict[str, Any] = field(default_factory=dict)
