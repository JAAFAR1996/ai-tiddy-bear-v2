from datetime import datetime
from enum import Enum
from typing import Any


class StateScope(Enum):
    REQUEST = "REQUEST"
    SESSION = "SESSION"
    APPLICATION = "APPLICATION"


class ApplicationStateManager:
    def __init__(self, use_redis: bool = False) -> None:
        self.use_redis = use_redis
        self.state: dict[str, Any] = {}

    async def set_state(
        self,
        key: str,
        value: Any,
        scope: StateScope,
        expires_at: datetime | None = None,
    ) -> None:
        self.state[key] = value

    async def get_state(self, key: str, scope: StateScope) -> Any | None:
        return self.state.get(key)

    async def has_state(self, key: str, scope: StateScope) -> bool:
        return key in self.state

    async def delete_state(self, key: str, scope: StateScope) -> None:
        if key in self.state:
            del self.state[key]

    async def async_request_context(self, request_id: str) -> Any:
        class AsyncContextManager:
            async def __aenter__(self_inner):
                return self_inner

            async def __aexit__(self_inner, exc_type, exc_val, exc_tb):
                pass

        return AsyncContextManager()

    def session_context(self, session_id: str):
        class ContextManager:
            def __enter__(self_inner):
                return self_inner

            def __exit__(self_inner, exc_type, exc_val, exc_tb):
                pass

        return ContextManager()


def create_state_manager(use_redis: bool = False) -> ApplicationStateManager:
    return ApplicationStateManager(use_redis)
