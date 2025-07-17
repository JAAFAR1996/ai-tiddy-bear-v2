from abc import ABC, abstractmethod
from uuid import UUID

from src.domain.value_objects.notification import NotificationRecord


class INotificationRepository(ABC):
    """Abstract interface for notification persistence operations."""

    @abstractmethod
    async def save_notification(self, notification: NotificationRecord) -> None:
        """Saves or updates a notification record."""

    @abstractmethod
    async def get_notification_by_id(
        self,
        notification_id: UUID,
    ) -> NotificationRecord | None:
        """Retrieves a notification record by its ID."""

    @abstractmethod
    async def get_notifications_for_recipient(
        self,
        recipient: str,
    ) -> list[NotificationRecord]:
        """Retrieves all notification records for a specific recipient."""

    @abstractmethod
    async def delete_notification(self, notification_id: UUID) -> bool:
        """Deletes a notification record by its ID."""
