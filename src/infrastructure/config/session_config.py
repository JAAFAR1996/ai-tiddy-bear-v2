from dataclasses import dataclass


@dataclass(slots=True, frozen=True)
class SessionConfig:
    """Configuration for session management.

    Attributes:
        session_timeout_minutes (int): The number of minutes after which a session expires due to inactivity.

    """

    session_timeout_minutes: int = 30
