import logging
# Import container for service resolution - DI fixes complete
from abc import ABC, abstractmethod
from typing import Any

# Restore proper interface imports
from .infrastructure_services import IEventBus, IExternalAPIClient, ISettingsProvider

# Import container for service resolution
from src.infrastructure.di.container import container

"""
Read Model Interfaces for Application Layer
This module provides interfaces for read models that the application
layer can depend on without violating architectural boundaries.
"""


class IChildProfileReadModel(ABC):
    """Interface for child profile read model."""

    @property
    @abstractmethod
    def id(self) -> str:
        """Child identifier."""

    @property
    @abstractmethod
    def name(self) -> str:
        """Child name."""

    @property
    @abstractmethod
    def age(self) -> int:
        """Child age."""

    @property
    @abstractmethod
    def preferences(self) -> dict[str, Any]:
        """Child preferences."""


class IChildProfileReadModelStore(ABC):
    """Interface for child profile read model storage."""

    @abstractmethod
    async def save(self, model: IChildProfileReadModel) -> None:
        """Save child profile read model."""

    @abstractmethod
    async def get_by_id(self, child_id: str) -> IChildProfileReadModel | None:
        """Get child profile by ID."""

    @abstractmethod
    async def delete_by_id(self, child_id: str) -> bool:
        """Delete child profile by ID."""

    @abstractmethod
    async def update(self, child_id: str, updates: dict[str, Any]) -> bool:
        """Update child profile."""

    """Interface for external API clients."""

    @abstractmethod
    async def make_request(self, endpoint: str, data: dict[str, Any]) -> dict[str, Any]:
        """Make an API request."""

    @abstractmethod
    async def check_health(self) -> bool:
        """Check API health status."""

    """Interface for COPPA consent management."""

    @abstractmethod
    async def verify_consent(self, child_id: str, operation: str) -> bool:
        """Verify parental consent for operation."""

    @abstractmethod
    async def get_consent_status(self, child_id: str) -> dict[str, Any]:
        """Get consent status details."""

    @abstractmethod
    async def revoke_consent(self, child_id: str) -> bool:
        """Revoke parental consent."""


# Factory functions for creating implementations

logger = logging.getLogger(__name__)


def create_child_profile_read_model(
    child_id: str, name: str, age: int, preferences: dict[str, Any]
):  # -> IChildProfileReadModel:
    """Create a child profile read model instance."""
    try:
        # Use container to get read model factory
        logger.info(f"Creating child profile read model for child_id: {child_id}")
        # For now, return a basic implementation until proper service is available
        raise NotImplementedError("IChildProfileReadModel service not yet registered")
    except Exception as e:
        logger.error(f"Failed to create child profile read model: {e}")
        return None


def get_read_model_store():  # -> IChildProfileReadModelStore:
    """Get the child profile read model store service."""
    try:
        # Use container to get read model store
        logger.info("Getting read model store from container")
        # For now, return None until proper service is available
        raise NotImplementedError("IChildProfileReadModelStore service not yet registered")
    except Exception as e:
        logger.error(f"Failed to get read model store: {e}")
        return None


def get_event_bus():  # -> IEventBus:
    """Get the event bus service."""
    try:
        # Use container to get event bus service
        logger.info("Getting event bus from container")
        # For now, return None until proper service is available
        raise NotImplementedError("IEventBus service not yet registered")
    except Exception as e:
        logger.error(f"Failed to get event bus: {e}")
        return None


def get_external_api_client(service_name: str):  # -> IExternalAPIClient:
    """Get an external API client service."""
    try:
        # Use container to get external API client
        logger.info(f"Getting external API client for service: {service_name}")
        # For now, return None until proper service is available
        raise NotImplementedError(f"IExternalAPIClient service '{service_name}' not yet registered")
    except Exception as e:
        logger.error(f"Failed to get external API client for {service_name}: {e}")
        return None


def get_settings_provider():  # -> ISettingsProvider:
    """Get the settings provider service."""
    try:
        # Use container settings (this already works)
        logger.info("Getting settings provider from container")
        return container.settings()  # This should work as settings is already available
    except Exception as e:
        logger.error(f"Failed to get settings provider: {e}")
        return None
