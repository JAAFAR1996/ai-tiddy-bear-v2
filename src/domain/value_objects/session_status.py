from enum import Enum


class SessionStatus(str, Enum):
    """Session status enumeration."""

    ACTIVE = "active"
    EXPIRED = "expired"
    ENDED = "ended"
    SUSPENDED = "suspended"
