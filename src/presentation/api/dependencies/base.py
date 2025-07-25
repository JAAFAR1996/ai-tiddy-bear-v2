"""Base dependency injection patterns."""

from abc import ABC, abstractmethod
from typing import Any, Callable, TypeVar

T = TypeVar("T")


class ServiceFactory(ABC):
    """Abstract factory for service creation."""

    @abstractmethod
    def create(self) -> Any:
        """Create service instance."""


class LazyServiceProvider:
    """Lazy service provider to avoid circular imports."""

    def __init__(self, factory: Callable[[], T]):
        self._factory = factory
        self._instance = None

    def get(self) -> T:
        if self._instance is None:
            self._instance = self._factory()
        return self._instance
