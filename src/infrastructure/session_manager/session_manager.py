import asyncio
from datetime import datetime, timedelta
from uuid import UUID, uuid4

from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from .session_models import Session, SessionStatus


class SessionConstants:
    DEFAULT_TIMEOUT_MINUTES = 30
    MAX_INACTIVE_TIME_MINUTES = 60


class SessionManager:
    def __init__(self, db_session: AsyncSession) -> None:
        self.db = db_session
        self._active_sessions = {}
        self._session_lock = asyncio.Lock()

    async def create_session(
        self, child_id: str, initial_data: dict | None = None
    ) -> UUID:
        session_id = uuid4()
        new_session = Session(
            id=str(session_id),
            child_id=child_id,
            session_data=str(initial_data) if initial_data else None,
        )
        self.db.add(new_session)
        await self.db.commit()
        await self.db.refresh(new_session)
        async with self._session_lock:
            self._active_sessions[session_id] = new_session
        return session_id

    async def get_session(self, session_id: UUID) -> Session:
        async with self._session_lock:
            if session_id in self._active_sessions:
                return self._active_sessions[session_id]
        result = await self.db.execute(
            select(Session).filter_by(id=str(session_id))
        )
        session = result.scalar_one_or_none()
        if session:
            async with self._session_lock:
                self._active_sessions[session.id] = session
        return session

    async def update_activity(self, session_id: UUID) -> bool:
        session = await self.get_session(session_id)
        if session:
            session.interaction_count += 1
            session.last_activity = datetime.utcnow()
            await self.db.commit()
            return True
        return False

    async def end_session(self, session_id: UUID, reason: str = "") -> bool:
        session = await self.get_session(session_id)
        if session:
            session.status = SessionStatus.ENDED.value
            session.ended_at = datetime.utcnow()
            session.end_reason = reason
            await self.db.commit()
            async with self._session_lock:
                if session_id in self._active_sessions:
                    del self._active_sessions[session_id]
            return True
        return False

    async def get_active_sessions(self) -> list[Session]:
        result = await self.db.execute(
            select(Session).filter_by(status=SessionStatus.ACTIVE.value),
        )
        return result.scalars().all()

    async def cleanup_inactive_sessions(
        self,
        timeout_minutes: int = SessionConstants.DEFAULT_TIMEOUT_MINUTES,
    ) -> int:
        timeout_threshold = datetime.utcnow() - timedelta(
            minutes=timeout_minutes
        )
        inactive_sessions = await self.db.execute(
            select(Session).filter(
                Session.status == SessionStatus.ACTIVE.value,
                Session.last_activity < timeout_threshold,
            ),
        )
        count = 0
        for session in inactive_sessions.scalars().all():
            session.status = SessionStatus.TIMEOUT.value
            session.ended_at = datetime.utcnow()
            session.end_reason = "timeout"
            count += 1
        await self.db.commit()
        return count

    async def get_session_stats(self) -> dict:
        active_count = await self.db.scalar(
            select(func.count()).filter_by(status=SessionStatus.ACTIVE.value),
        )
        total_today = await self.db.scalar(
            select(func.count()).filter(
                Session.created_at >= datetime.utcnow().date()
            ),
        )
        return {
            "active_sessions": active_count,
            "sessions_today": total_today,
            "memory_cache_size": len(self._active_sessions),
            "session_timeout_minutes": SessionConstants.DEFAULT_TIMEOUT_MINUTES,
        }
