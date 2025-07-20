import json
from datetime import datetime, timedelta

from redis.asyncio import Redis

from src.application.services.session_manager import SessionData
from src.domain.interfaces.session_repository import ISessionRepository
from src.infrastructure.config.session_config import SessionConfig
from src.infrastructure.logging_config import get_logger

logger = get_logger(__name__, component="redis_session_repository")


class RedisSessionRepository(ISessionRepository):
    """Redis implementation of the session repository.
    Stores session data in Redis, leveraging its key-value store and expiration capabilities.
    """

    SESSION_KEY_PREFIX = "session:"

    def __init__(self, redis_client: Redis, session_config: SessionConfig) -> None:
        self.redis_client = redis_client
        self.session_config = session_config
        self.logger = logger

    async def get(self, session_id: str) -> SessionData | None:
        key = self.SESSION_KEY_PREFIX + session_id
        try:
            session_data_json = await self.redis_client.get(key)
            if session_data_json:
                session_data_dict = json.loads(session_data_json)
                session_data = SessionData(
                    child_id=session_data_dict["child_id"],
                    session_id=session_data_dict["session_id"],
                    created_at=datetime.fromisoformat(session_data_dict["created_at"]),
                    last_activity=datetime.fromisoformat(
                        session_data_dict["last_activity"],
                    ),
                    data=session_data_dict.get("data", {}),
                )
                self.logger.debug(f"Retrieved session {session_id} from Redis.")
                return session_data
            self.logger.debug(f"Session {session_id} not found in Redis.")
            return None
        except Exception as e:
            self.logger.error(
                f"Error getting session {session_id} from Redis: {e}",
                exc_info=True,
            )
            return None

    async def save(self, session_data: SessionData, timeout_minutes: int) -> None:
        key = self.SESSION_KEY_PREFIX + session_data.session_id
        try:
            # Convert datetime objects to ISO format strings for JSON
            # serialization
            session_data_dict = {
                "child_id": session_data.child_id,
                "session_id": session_data.session_id,
                "created_at": session_data.created_at.isoformat(),
                "last_activity": session_data.last_activity.isoformat(),
                "data": session_data.data,
            }
            await self.redis_client.setex(
                key,
                timedelta(minutes=timeout_minutes),
                json.dumps(session_data_dict),
            )
            self.logger.debug(
                f"Saved session {session_data.session_id} to Redis with timeout {timeout_minutes} min.",
            )
        except Exception as e:
            self.logger.error(
                f"Error saving session {session_data.session_id} to Redis: {e}",
                exc_info=True,
            )
            raise  # Re-raise to ensure calling service handles persistence failure

    async def delete(self, session_id: str) -> bool:
        key = self.SESSION_KEY_PREFIX + session_id
        try:
            result = await self.redis_client.delete(key)
            if result > 0:
                self.logger.debug(f"Deleted session {session_id} from Redis.")
                return True
            self.logger.debug(f"Session {session_id} not found for deletion in Redis.")
            return False
        except Exception as e:
            self.logger.error(
                f"Error deleting session {session_id} from Redis: {e}",
                exc_info=True,
            )
            return False

    async def delete_expired(self, timeout_minutes: int) -> None:
        # Redis handles expiration automatically via SETEX, so explicit mass deletion of expired
        # sessions is not typically needed. However, if there were a need to clean up sessions
        # that somehow outlived their SETEX (e.g., due to Redis restart without AOF/RDB sync),
        # a scan and check approach would be used here. For simplicity and leveraging SETEX,
        # this method can log that explicit cleanup is handled by Redis's TTL.
        self.logger.info(
            "Redis handles session expiration automatically. Explicit delete_expired not required.",
        )
