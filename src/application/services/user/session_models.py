"""Session Data Models
Defines core data structures for async session management.
"""

import uuid
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from enum import Enum
from typing import Any


class SessionStatus(str, Enum):
    """Session status enumeration."""

    ACTIVE = "active"
    EXPIRED = "expired"
    ENDED = "ended"
    SUSPENDED = "suspended"


@dataclass
class AsyncSessionData:
    """Features:
    - Automatic expiration tracking
    - Activity monitoring
    - Child safety score tracking
    - COPPA-compliant data handling.
    """

    session_id: str = field(default_factory=lambda: str(uuid.uuid4()))
    child_id: str = ""
    created_at: datetime = field(default_factory=datetime.utcnow)
    last_activity: datetime = field(default_factory=datetime.utcnow)
    status: SessionStatus = SessionStatus.ACTIVE
    data: dict[str, Any] = field(default_factory=dict)
    metadata: dict[str, Any] = field(default_factory=dict)
    interaction_count: int = 0
    safety_score: float = 1.0

    def is_expired(self, timeout_minutes: int = 30) -> bool:
        """Check if session is expired based on inactivity."""
        if self.status != SessionStatus.ACTIVE:
            return True

        timeout_delta = timedelta(minutes=timeout_minutes)
        return datetime.utcnow() - self.last_activity > timeout_delta

    def update_activity(self) -> None:
        """Update last activity timestamp."""
        self.last_activity = datetime.utcnow()
        self.interaction_count += 1

    def get_session_duration(self) -> timedelta:
        """Get total session duration."""
        return self.last_activity - self.created_at

    def to_dict(self) -> dict[str, Any]:
        """Convert session data to dictionary for serialization."""
        return {
            "session_id": self.session_id,
            "child_id": self.child_id,
            "created_at": self.created_at.isoformat(),
            "last_activity": self.last_activity.isoformat(),
            "status": self.status.value,
            "data": self.data,
            "metadata": self.metadata,
            "interaction_count": self.interaction_count,
            "safety_score": self.safety_score,
        }


@dataclass
class SessionStats:
    """Session statistics container."""

    total_sessions: int = 0
    active_sessions: int = 0
    expired_sessions: int = 0
    average_duration_minutes: float = 0.0
    total_interactions: int = 0
    average_safety_score: float = 1.0
