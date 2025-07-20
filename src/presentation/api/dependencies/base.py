"""Base dependency injection patterns."""
from functools import lru_cache
from typing import TypeVar, Callable, Any
from abc import ABC, abstractmethod

T = TypeVar('T')

class ServiceFactory(ABC):
    """Abstract factory for service creation."""
    
    @abstractmethod
    def create(self) -> Any:
        """Create service instance."""
        pass

class LazyServiceProvider:
    """Lazy service provider to avoid circular imports."""
    
    def __init__(self, factory: Callable[[], T]):
        self._factory = factory
        self._instance = None
    
    def get(self) -> T:
        if self._instance is None:
            self._instance = self._factory()
        return self._instance
