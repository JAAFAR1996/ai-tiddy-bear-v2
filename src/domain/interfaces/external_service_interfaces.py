"""External service interfaces for the domain layer.
These interfaces define contracts for external services without
creating dependencies on specific implementations.
"""

from abc import ABC, abstractmethod
from typing import Any
from uuid import UUID


class IAIService(ABC):
    """Interface for AI service operations."""

    @abstractmethod
    async def generate_response(
        self,
        child_id: UUID,
        conversation_history: list[str],
        current_input: str,
        preferences: dict[str, Any],
    ) -> dict[str, Any]:
        """Generate an AI response for a child."""

    @abstractmethod
    async def validate_content_safety(self, content: str) -> dict[str, Any]:
        """Validate content for child safety."""


class INotificationService(ABC):
    """Interface for notification operations."""

    @abstractmethod
    async def send_parent_notification(
        self,
        parent_id: UUID,
        message: str,
        notification_type: str,
        metadata: dict[str, Any] | None = None,
    ) -> bool:
        """Send a notification to a parent."""

    @abstractmethod
    async def send_safety_alert(
        self,
        parent_id: UUID,
        child_id: UUID,
        alert_details: dict[str, Any],
    ) -> bool:
        """Send a safety alert notification."""
