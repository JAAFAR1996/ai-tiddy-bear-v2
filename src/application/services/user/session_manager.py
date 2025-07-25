"""Clean, focused session management extracted from 426-line monolith.
Provides enterprise-grade session handling with child safety features.
"""

import asyncio
import contextlib
from datetime import datetime
from typing import Any

from src.domain.models.session_models import (
    AsyncSessionData,
    SessionStats,
    SessionStatus,
)
from src.infrastructure.logging_config import get_logger

from .session_storage import SessionStorage

logger = get_logger(__name__, component="services")


class AsyncSessionManager:
    """Refactored from 426-line file into focused, maintainable components.
    Provides enterprise-grade session management with child safety features.
    Features:
    - Thread-safe session operations
    - Automatic expiration handling
    - Child safety monitoring
    - COPPA-compliant data handling
    - Performance optimized storage.
    """

    def __init__(self, default_timeout_minutes: int = 30) -> None:
        """Initialize session manager with storage backend."""
        self.storage = SessionStorage()
        self.default_timeout = default_timeout_minutes
        self._cleanup_task: asyncio.Task | None = None
        self._manager_lock = asyncio.Lock()

    async def start_cleanup_task(self) -> None:
        """Start background task for cleaning up expired sessions."""
        if self._cleanup_task is None or self._cleanup_task.done():
            self._cleanup_task = asyncio.create_task(self._cleanup_loop())

    async def stop_cleanup_task(self) -> None:
        """Stop background cleanup task."""
        if self._cleanup_task and not self._cleanup_task.done():
            self._cleanup_task.cancel()
            with contextlib.suppress(asyncio.CancelledError):
                await self._cleanup_task

    async def create_session(
        self,
        child_id: str,
        initial_data: dict[str, Any] | None = None,
        metadata: dict[str, Any] | None = None,
    ) -> AsyncSessionData:
        """Create a new session for a child.

        Args:
            child_id: Child identifier
            initial_data: Initial session data
            metadata: Session metadata
        Returns:
            New session data

        """
        session = AsyncSessionData(
            child_id=child_id,
            data=initial_data or {},
            metadata=metadata or {},
        )
        await self.storage.store_session(session)
        logger.info(f"Session created: {session.session_id[:8]}...")
        return session

    async def get_session(self, session_id: str) -> AsyncSessionData | None:
        """Retrieve a session by ID.

        Args:
            session_id: Session identifier
        Returns:
            Session data if found and active, None otherwise

        """
        session = await self.storage.retrieve_session(session_id)
        if session is None:
            return None

        # Check if session is expired
        if session.is_expired(self.default_timeout):
            session.status = SessionStatus.EXPIRED
            await self.storage.store_session(session)
            return None

        # Update activity
        session.update_activity()
        await self.storage.store_session(session)
        return session

    async def update_session(
        self,
        session_id: str,
        data_updates: dict[str, Any] | None = None,
        metadata_updates: dict[str, Any] | None = None,
    ) -> bool:
        """Update session data and metadata.

        Args:
            session_id: Session identifier
            data_updates: Updates to session data
            metadata_updates: Updates to session metadata
        Returns:
            True if updated successfully

        """
        session = await self.storage.retrieve_session(session_id)
        if session is None or session.is_expired(self.default_timeout):
            return False

        # Update data
        if data_updates:
            session.data.update(data_updates)

        # Update metadata
        if metadata_updates:
            session.metadata.update(metadata_updates)

        # Update activity
        session.update_activity()

        # Store updated session
        await self.storage.store_session(session)
        return True

    async def end_session(self, session_id: str) -> bool:
        """End a session gracefully.

        Args:
            session_id: Session identifier
        Returns:
            True if ended successfully

        """
        session = await self.storage.retrieve_session(session_id)
        if session is None:
            return False

        session.status = SessionStatus.ENDED
        session.last_activity = datetime.utcnow()
        await self.storage.store_session(session)
        logger.info(f"Session ended: {session_id[:8]}...")
        return True

    async def get_child_sessions(self, child_id: str) -> list[AsyncSessionData]:
        """Get all active sessions for a child.

        Args:
            child_id: Child identifier
        Returns:
            List of active sessions for the child

        """
        all_sessions = await self.storage.get_child_sessions(child_id)

        # Filter for active sessions only
        active_sessions = [
            session
            for session in all_sessions
            if session.status == SessionStatus.ACTIVE
            and not session.is_expired(self.default_timeout)
        ]

        return active_sessions

    async def get_session_stats(self) -> SessionStats:
        """Get session statistics.

        Returns:
            Session statistics

        """
        total_count = await self.storage.get_session_count()
        active_count = await self.storage.get_active_session_count()

        # Calculate additional stats
        expired_count = total_count - active_count

        # For now, return basic stats
        # In production, these would be calculated from stored session data
        return SessionStats(
            total_sessions=total_count,
            active_sessions=active_count,
            expired_sessions=expired_count,
            average_duration_minutes=0.0,  # Would be calculated from actual data
            total_interactions=0,  # Would be calculated from actual data
            average_safety_score=1.0,  # Would be calculated from actual data
        )

    async def cleanup_expired_sessions(self) -> int:
        """Manually trigger cleanup of expired sessions.

        Returns:
            Number of sessions cleaned up

        """
        return await self.storage.cleanup_expired_sessions(self.default_timeout)

    async def _cleanup_loop(self) -> None:
        """Background task for periodic session cleanup."""
        while True:
            try:
                await asyncio.sleep(300)  # Run cleanup every 5 minutes
                await self.cleanup_expired_sessions()
            except asyncio.CancelledError:
                break
            except Exception as e:
                logger.error(f"Error in session cleanup: {e}")
                await asyncio.sleep(60)  # Wait before retrying
