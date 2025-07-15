"""
Provides an asynchronous session manager for handling user sessions.

This module has been refactored into a clean, modular architecture.
The original functionality is preserved while improving maintainability and adding
protection against race conditions.

**Migration Note**: For new code, import from the 'session' package:

```python
from src.application.services.session import AsyncSessionManager
```
"""

from .session.session_manager import AsyncSessionManager
from .session.session_models import (
    AsyncSessionData,
    SessionStatus,
    SessionStats,
)
from .session.session_storage import SessionStorage

# Re-export for backward compatibility
__all__ = [
    "AsyncSessionManager",
    "SessionStorage",
    "AsyncSessionData",
    "SessionStatus",
    "SessionStats",
]


def def get_session_manager(timeout_minutes: int = 30) -> AsyncSessionManager:
    """
    Factory function to create an AsyncSessionManager instance.

    Args:
        timeout_minutes: Default session timeout in minutes.

    Returns:
        A configured session manager instance.
    """
    return AsyncSessionManager(default_timeout_minutes=timeout_minutes)


def def get_session_storage() -> SessionStorage:
    """
    Factory function to create a SessionStorage instance.

    Returns:
        A configured session storage instance.
    """
    return SessionStorage()
