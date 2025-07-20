"""Session Storage Manager
Handles persistent storage and retrieval of session data.
"""

import asyncio

from src.infrastructure.logging_config import get_logger

from .session_models import AsyncSessionData, SessionStatus

logger = get_logger(__name__, component="services")


class SessionStorage:
    """Manages session persistence with thread-safe operations and automatic cleanup of expired sessions."""

    def __init__(self) -> None:
        """Initialize session storage with thread safety."""
        self.sessions: dict[str, AsyncSessionData] = {}
        self.child_sessions: dict[str, list[str]] = {}  # child_id -> session_ids
        self._storage_lock = asyncio.Lock()

    async def store_session(self, session: AsyncSessionData) -> bool:
        """Store a session with thread safety.

        Args:
            session: Session data to store
        Returns:
            True if stored successfully

        """
        async with self._storage_lock:
            self.sessions[session.session_id] = session

            # Track sessions by child ID
            if session.child_id:
                if session.child_id not in self.child_sessions:
                    self.child_sessions[session.child_id] = []

                if session.session_id not in self.child_sessions[session.child_id]:
                    self.child_sessions[session.child_id].append(session.session_id)

        return True

    async def retrieve_session(self, session_id: str) -> AsyncSessionData | None:
        """Retrieve a session by ID.

        Args:
            session_id: Session identifier
        Returns:
            Session data if found, None otherwise

        """
        async with self._storage_lock:
            return self.sessions.get(session_id)

    async def remove_session(self, session_id: str) -> bool:
        """Remove a session from storage.

        Args:
            session_id: Session identifier
        Returns:
            True if removed successfully

        """
        async with self._storage_lock:
            if session_id not in self.sessions:
                return False

            session = self.sessions[session_id]

            # Remove from sessions
            del self.sessions[session_id]

            # Remove from child sessions tracking
            if session.child_id and session.child_id in self.child_sessions:
                if session_id in self.child_sessions[session.child_id]:
                    self.child_sessions[session.child_id].remove(session_id)

                # Clean up empty child session list
                if not self.child_sessions[session.child_id]:
                    del self.child_sessions[session.child_id]

        return True

    async def get_child_sessions(self, child_id: str) -> list[AsyncSessionData]:
        """Get all sessions for a specific child.

        Args:
            child_id: Child identifier
        Returns:
            List of session data for the child

        """
        async with self._storage_lock:
            if child_id not in self.child_sessions:
                return []

            sessions = []
            for session_id in self.child_sessions[child_id]:
                if session_id in self.sessions:
                    sessions.append(self.sessions[session_id])

            return sessions

    async def cleanup_expired_sessions(self, timeout_minutes: int = 30) -> int:
        """Clean up expired sessions.

        Args:
            timeout_minutes: Session timeout in minutes
        Returns:
            Number of sessions cleaned up

        """
        expired_count = 0
        expired_session_ids = []

        async with self._storage_lock:
            for session_id, session in self.sessions.items():
                if session.is_expired(timeout_minutes):
                    expired_session_ids.append(session_id)
                    session.status = SessionStatus.EXPIRED

        # Remove expired sessions
        for session_id in expired_session_ids:
            await self.remove_session(session_id)
            expired_count += 1

        if expired_count > 0:
            logger.info(f"Cleaned up {expired_count} expired sessions")

        return expired_count

    async def get_session_count(self) -> int:
        """Get total number of active sessions.

        Returns:
            Number of active sessions

        """
        async with self._storage_lock:
            return len(self.sessions)

    async def get_active_session_count(self) -> int:
        """Get number of active (non-expired) sessions.

        Returns:
            Number of active sessions

        """
        active_count = 0

        async with self._storage_lock:
            for session in self.sessions.values():
                if session.status == SessionStatus.ACTIVE and not session.is_expired():
                    active_count += 1

        return active_count
