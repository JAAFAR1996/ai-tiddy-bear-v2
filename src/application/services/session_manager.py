"""
Manages user sessions, including creation, retrieval, and cleanup.

This service provides functionalities for handling session data, tracking
user activity, and automatically cleaning up expired sessions. It ensures
that user interactions are maintained within a defined session lifecycle.
"""

import uuid
from datetime import datetime, timedelta, timezone
from typing import Any, Optional
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
    client_ip: Optional[str] = None
    user_agent: Optional[str] = None

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

    async def create_session(self, child_id: str, client_ip: Optional[str] = None, user_agent: Optional[str] = None) -> SessionData:
        """
        Creates a new session for a child and saves it to the repository.

        Args:
            child_id: The ID of the child for whom to create the session.
            client_ip: The IP address of the client creating the session.
            user_agent: The User-Agent string of the client creating the session.

        Returns:
            The newly created SessionData object.
        """
        session = SessionData(child_id=child_id, client_ip=client_ip, user_agent=user_agent)
        await self.session_repository.save(session, self.session_config.session_timeout_minutes)
        self.logger.info(f"Session created for child_id: {child_id}, session_id: {session.session_id}, IP: {client_ip}, UA: {user_agent}")
        return session

    async def get_session(self, session_id: str, client_ip: Optional[str] = None, user_agent: Optional[str] = None) -> SessionData | None:
        """
        Retrieves a session by its ID from the repository, with enhanced security checks.

        Args:
            session_id: The ID of the session to retrieve.
            client_ip: The current IP address of the client making the request.
            user_agent: The current User-Agent string of the client making the request.

        Returns:
            The SessionData object if found, valid, and not expired, otherwise None.
        """
        session = await self.session_repository.get(session_id)
        if not session:
            self.logger.debug(f"Session {session_id} not found.")
            return None

        if session.is_expired(timeout_minutes=self.session_config.session_timeout_minutes):
            self.logger.info(f"Session {session_id} expired. Deleting.")
            await self.session_repository.delete(session_id)
            return None

        if session.client_ip and client_ip and session.client_ip != client_ip:
            self.logger.warning(f"Session hijacking attempt detected for session {session_id}. IP mismatch: stored {session.client_ip}, current {client_ip}. Invalidating session.")
            await self.session_repository.delete(session_id)
            return None
        
        if session.user_agent and user_agent and session.user_agent != user_agent:
            self.logger.warning(f"Session hijacking attempt detected for session {session_id}. User-Agent mismatch: stored '{session.user_agent}', current '{user_agent}'. Invalidating session.")
            await self.session_repository.delete(session_id)
            return None

        session.update_activity()
        await self.session_repository.save(session, self.session_config.session_timeout_minutes)
        self.logger.debug(f"Session {session_id} retrieved and activity updated.")
        return session

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
