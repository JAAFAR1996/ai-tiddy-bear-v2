"""Infrastructure configuration module."""

# Import get_settings function only to avoid circular imports
from .settings import get_settings

__all__ = [
    "get_settings",
]
