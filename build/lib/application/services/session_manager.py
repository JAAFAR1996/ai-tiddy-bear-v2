"""
Manages user sessions, including creation, retrieval, and cleanup.

This service provides functionalities for handling session data, tracking
user activity, and automatically cleaning up expired sessions. It ensures
that user interactions are maintained within a defined session lifecycle.
"""

import uuid
from datetime import datetime, timedelta, timezone
from typing import Any
from dataclasses import dataclass, field
from src.infrastructure.config.session_config import SessionConfig
from src.domain.interfaces.session_repository import ISessionRepository
from src.infrastructure.logging_config import get_logger


@dataclass(slots=True)
class SessionData:
    """Container for session-specific data."""

    child_id: str
    session_id: str = field(default_factory=lambda: str(uuid.uuid4()))
    created_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
    last_activity: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
    data: dict[str, Any] = field(default_factory=dict)

    def is_expired(self, timeout_minutes: int) -> bool:
        """
        Checks if the session has expired based on inactivity.

        Args:
            timeout_minutes: The number of minutes after which a session expires due to inactivity.

        Returns:
            True if the session is expired, False otherwise.
        """
        return datetime.now(timezone.utc) - self.last_activity > timedelta(minutes=timeout_minutes)

    def update_activity(self) -> None:
        """
        Updates the last activity timestamp of the session.
        """
        self.last_activity = datetime.now(timezone.utc)


class SessionManager:
    """Manages user sessions."""

    def __init__(
        self,
        session_config: SessionConfig,
        session_repository: ISessionRepository,
    ) -> None:
        """
        Initializes the session manager with configuration.

        Args:
            session_config: Configuration for session timeout and other settings.
            session_repository: The repository for persisting session data.
        """
        self.session_config = session_config
        self.session_repository = session_repository
        self.logger = get_logger(__name__, component="session_manager")
        # self.sessions: dict[str, SessionData] = {}

    async def create_session(self, child_id: str) -> SessionData:
        """
        Creates a new session for a child and saves it to the repository.

        Args:
            child_id: The ID of the child for whom to create the session.

        Returns:
            The newly created SessionData object.
        """
        session = SessionData(child_id)
        await self.session_repository.save(session, self.session_config.session_timeout_minutes)
        self.logger.info(f"Session created for child_id: {child_id}, session_id: {session.session_id}")
        return session

    async def get_session(self, session_id: str) -> SessionData | None:
        """
        Retrieves a session by its ID from the repository.

        Args:
            session_id: The ID of the session to retrieve.

        Returns:
            The SessionData object if found and not expired, otherwise None.
        """
        session = await self.session_repository.get(session_id)
        if session and not session.is_expired(timeout_minutes=self.session_config.session_timeout_minutes):
            session.update_activity()
            await self.session_repository.save(session, self.session_config.session_timeout_minutes) # Save updated activity
            self.logger.debug(f"Session {session_id} retrieved and activity updated.")
            return session
        elif session: # Session exists but is expired, delete it from repository
            self.logger.info(f"Session {session_id} found but expired. Deleting.")
            await self.session_repository.delete(session_id)
        else:
            self.logger.debug(f"Session {session_id} not found.")
        return None

    async def end_session(self, session_id: str) -> bool:
        """
        Ends a session by deleting it from the repository.

        Args:
            session_id: The ID of the session to end.

        Returns:
            True if the session was successfully ended, False otherwise.
        """
        success = await self.session_repository.delete(session_id)
        if success:
            self.logger.info(f"Session {session_id} successfully ended.")
        else:
            self.logger.warning(f"Attempted to end session {session_id}, but it was not found.")
        return success

    async def cleanup_expired_sessions(self) -> None:
        """
        Triggers the repository to remove all expired sessions.
        """
        self.logger.info("Initiating cleanup of expired sessions.")
        await self.session_repository.delete_expired(self.session_config.session_timeout_minutes)
        self.logger.info("Expired session cleanup triggered successfully.")
