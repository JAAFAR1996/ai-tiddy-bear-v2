import logging
from src.infrastructure.di.container import container
from abc import ABC, abstractmethod
from typing import Any

"""

from .infrastructure_services import IEventBus, IExternalAPIClient, IConsentManager

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
) -> IChildProfileReadModel:
    """Factory function for creating child profile read models (production)."""
    try:
        return container.child_profile_read_model_factory(
            child_id=child_id, name=name, age=age, preferences=preferences
        )
    except Exception as e:
        logger.error(f"Failed to create child profile read model: {e}")
        raise


def get_read_model_store() -> IChildProfileReadModelStore:
    """Factory function for getting read model store (production)."""
    try:
        return container.child_profile_read_model_store()
    except Exception as e:
        logger.error(f"Failed to get read model store: {e}")
        raise


def get_event_bus() -> IEventBus:
    """Factory function for getting event bus (production)."""
    try:
        return container.event_bus()
    except Exception as e:
        logger.error(f"Failed to get event bus: {e}")
        raise


def get_external_api_client(service_name: str) -> IExternalAPIClient:
    """Factory function for getting external API client (production)."""
    try:
        return container.external_api_client(service_name=service_name)
    except Exception as e:
        logger.error(f"Failed to get external API client: {e}")
        raise


def get_settings_provider() -> ISettingsProvider:
    """Factory function for getting settings provider (production)."""
    try:
        return container.settings_provider()
    except Exception as e:
        logger.error(f"Failed to get settings provider: {e}")
        raise
