from abc import ABC, abstractmethod
from typing import List, Optional
from uuid import UUID

from src.domain.value_objects.notification import NotificationRecord


class INotificationRepository(ABC):
    """
    Abstract interface for notification persistence operations.
    """

    @abstractmethod
    async def save_notification(self, notification: NotificationRecord) -> None:
        """
        Saves or updates a notification record.
        """
        pass

    @abstractmethod
    async def get_notification_by_id(self, notification_id: UUID) -> Optional[NotificationRecord]:
        """
        Retrieves a notification record by its ID.
        """
        pass

    @abstractmethod
    async def get_notifications_for_recipient(self, recipient: str) -> List[NotificationRecord]:
        """
        Retrieves all notification records for a specific recipient.
        """
        pass

    @abstractmethod
    async def delete_notification(self, notification_id: UUID) -> bool:
        """
        Deletes a notification record by its ID.
        """
        pass 