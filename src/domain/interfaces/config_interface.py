"""Configuration Interface for Domain Layer
This interface provides access to configuration without infrastructure dependencies.
"""

from abc import ABC, abstractmethod
from typing import Any


class ConfigInterface(ABC):
    """Interface for configuration services."""

    @abstractmethod
    def get(self, key: str, default: Any = None) -> Any:
        """Get configuration value by key."""

    @abstractmethod
    def get_bool(self, key: str, default: bool = False) -> bool:
        """Get boolean configuration value."""

    @abstractmethod
    def get_int(self, key: str, default: int = 0) -> int:
        """Get integer configuration value."""

    @abstractmethod
    def get_str(self, key: str, default: str = "") -> str:
        """Get string configuration value."""
