"""Application Container - Professional DI Implementation
Following SOLID principles and Clean Architecture patterns.
"""
from typing import TypeVar, Type, Dict, Any, Optional, Protocol
from abc import ABC, abstractmethod
import threading
from functools import lru_cache

from src.infrastructure.config.settings import Settings, get_settings
from src.infrastructure import dependencies
from src.infrastructure.validators.config.startup_validator import StartupValidator
from src.infrastructure.logging_config import get_logger

logger = get_logger(__name__)

T = TypeVar('T')

class IContainer(Protocol):
    """Container interface following Interface Segregation Principle."""
    
    def register(self, interface: Type[T], factory: Any) -> None:
        """Register a service factory."""
        ...
    
    def resolve(self, interface: Type[T]) -> T:
        """Resolve a service instance."""
        ...
    
    def wire(self, modules: list[str]) -> None:
        """Wire dependencies for specified modules."""
        ...

class ServiceRegistry:
    """Thread-safe service registry."""
    
    def __init__(self):
        self._factories: Dict[Type, Any] = {}
        self._instances: Dict[Type, Any] = {}
        self._lock = threading.RLock()
    
    def register_factory(self, interface: Type[T], factory: Any) -> None:
        """Register a factory for an interface."""
        with self._lock:
            self._factories[interface] = factory
            logger.debug(f"Registered factory for {interface if isinstance(interface, str) else interface.__name__}")
    
    def register_singleton(self, interface: Type[T], instance: T) -> None:
        """Register a singleton instance."""
        with self._lock:
            self._instances[interface] = instance
            logger.debug(f"Registered singleton for {interface.__name__}")
    
    def resolve(self, interface: Type[T]) -> T:
        """Resolve a service, creating if necessary."""
        with self._lock:
            # Check for existing instance
            if interface in self._instances:
                return self._instances[interface]
            
            # Check for factory
            if interface in self._factories:
                instance = self._factories[interface]()
                self._instances[interface] = instance
                return instance
            
            raise ValueError(f"No registration found for {interface.__name__}")
    
    def clear(self) -> None:
        """Clear all registrations."""
        with self._lock:
            self._factories.clear()
            self._instances.clear()

class ApplicationContainer(IContainer):
    """Main application container with professional DI implementation."""
    
    _instance: Optional['ApplicationContainer'] = None
    _lock = threading.Lock()
    
    def __new__(cls):
        """Singleton pattern implementation."""
        if cls._instance is None:
            with cls._lock:
                if cls._instance is None:
                    cls._instance = super().__new__(cls)
        return cls._instance
    
    def __init__(self):
        """Initialize container with service registry."""
        if not hasattr(self, '_initialized'):
            self._registry = ServiceRegistry()
            self._settings: Optional[Settings] = None
            self._wired_modules: set[str] = set()
            self._initialized = True
            self._setup_core_services()
    
    def _setup_core_services(self) -> None:
        """Register core application services."""
        # Settings
        self._registry.register_factory(
            Settings,
            lambda: self.settings()
        )
        
        # Startup Validator
        self._registry.register_factory(
            StartupValidator,
            self._create_startup_validator
        )
        
        # Application Use Cases
        self._registry.register_factory(
            "manage_child_profile_use_case",
            dependencies.get_manage_child_profile_use_case
        )
        logger.info("Core services registered")
    
    def _create_startup_validator(self) -> StartupValidator:
        """Factory method for creating StartupValidator."""
        # StartupValidator expects Settings via Depends in __init__
        # For manual instantiation, we pass it directly
        return StartupValidator(settings=self.settings())
    
    @lru_cache(maxsize=1)
    def settings(self) -> Settings:
        """Get or create settings instance."""
        if self._settings is None:
            self._settings = get_settings()
        return self._settings
    
    def startup_validator(self) -> StartupValidator:
        """Get startup validator instance."""
        return self._registry.resolve(StartupValidator)
    
    def register(self, interface: Type[T], factory: Any) -> None:
        """Register a service factory."""
        self._registry.register_factory(interface, factory)
    
    def resolve(self, interface: Type[T]) -> T:
        """Resolve a service instance."""
        return self._registry.resolve(interface)
    
    def wire(self, modules: list[str]) -> None:
        """Wire dependencies for specified modules."""
        for module in modules:
            if module not in self._wired_modules:
                logger.info(f"Wiring module: {module}")
                self._wired_modules.add(module)
                # Actual wiring implementation would go here
                # For now, just log it
        
        logger.info(f"Wired {len(modules)} modules")
    
    def reset(self) -> None:
        """Reset container state (useful for testing)."""
        self._registry.clear()
        self._settings = None
        self._wired_modules.clear()
        self._setup_core_services()

# Global container instance
container = ApplicationContainer()

# Export convenience functions
def get_container() -> ApplicationContainer:
    """Get the application container instance."""
    return container

def register_service(interface: Type[T], factory: Any) -> None:
    """Register a service in the global container."""
    container.register(interface, factory)

def resolve_service(interface: Type[T]) -> T:
    """Resolve a service from the global container."""
    return container.resolve(interface)
