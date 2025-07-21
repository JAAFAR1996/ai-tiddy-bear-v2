import json
from datetime import datetime
from uuid import UUID

from redis.asyncio import Redis

from src.domain.interfaces.notification_repository import (
    INotificationRepository,
)
from src.domain.value_objects.notification import (
    NotificationRecord,
    NotificationStatus,
)
from src.infrastructure.logging_config import get_logger

logger = get_logger(__name__, component="redis_notification_repository")


class RedisNotificationRepository(INotificationRepository):
    """Redis implementation of the notification repository.
    Stores notification records in Redis.
    """

    NOTIFICATION_KEY_PREFIX = "notification:"
    RECIPIENT_HISTORY_KEY_PREFIX = "notification_history:"

    def __init__(self, redis_client: Redis) -> None:
        self.redis_client = redis_client
        self.logger = logger

    async def save_notification(self, notification: NotificationRecord) -> None:
        key = self.NOTIFICATION_KEY_PREFIX + str(notification.id)
        history_key = self.RECIPIENT_HISTORY_KEY_PREFIX + notification.recipient
        try:
            notification_data_dict = {
                "id": str(notification.id),
                "recipient": notification.recipient,
                "message": notification.message,
                "notification_type": notification.notification_type,
                "channel": notification.channel,
                "urgent": notification.urgent,
                "created_at": notification.created_at.isoformat(),
                "status": notification.status.value,
                "attempts": notification.attempts,
                "max_attempts": notification.max_attempts,
                "last_attempt_at": (
                    notification.last_attempt_at.isoformat()
                    if notification.last_attempt_at
                    else None
                ),
                "error_message": notification.error_message,
                "metadata": notification.metadata,
            }
            await self.redis_client.set(key, json.dumps(notification_data_dict))
            # Store in recipient's history (e.g., as a list of IDs or a ZSET for ordering)
            # For simplicity, using a list of IDs for now, or could use hset
            # for a smaller set of recent items
            await self.redis_client.lpush(history_key, str(notification.id))
            await self.redis_client.ltrim(
                history_key,
                0,
                99,
            )  # Keep last 100 notifications per recipient
            self.logger.debug(
                f"Saved notification {notification.id} for recipient {notification.recipient} to Redis.",
            )
        except Exception as e:
            self.logger.error(
                f"Error saving notification {notification.id} to Redis: {e}",
                exc_info=True,
            )
            raise  # Re-raise to ensure calling service handles persistence failure

    async def get_notification_by_id(
        self,
        notification_id: UUID,
    ) -> NotificationRecord | None:
        key = self.NOTIFICATION_KEY_PREFIX + str(notification_id)
        try:
            notification_data_json = await self.redis_client.get(key)
            if notification_data_json:
                notification_data_dict = json.loads(notification_data_json)
                notification = NotificationRecord(
                    id=UUID(notification_data_dict["id"]),
                    recipient=notification_data_dict["recipient"],
                    message=notification_data_dict["message"],
                    notification_type=notification_data_dict["notification_type"],
                    channel=notification_data_dict["channel"],
                    urgent=notification_data_dict["urgent"],
                    created_at=datetime.fromisoformat(
                        notification_data_dict["created_at"],
                    ),
                    status=NotificationStatus[notification_data_dict["status"].upper()],
                    attempts=notification_data_dict.get("attempts", 0),
                    max_attempts=notification_data_dict.get("max_attempts", 3),
                    last_attempt_at=(
                        datetime.fromisoformat(
                            notification_data_dict["last_attempt_at"],
                        )
                        if notification_data_dict.get("last_attempt_at")
                        else None
                    ),
                    error_message=notification_data_dict.get("error_message"),
                    metadata=notification_data_dict.get("metadata", {}),
                )
                self.logger.debug(
                    f"Retrieved notification {notification_id} from Redis.",
                )
                return notification
            self.logger.debug(f"Notification {notification_id} not found in Redis.")
            return None
        except Exception as e:
            self.logger.error(
                f"Error getting notification {notification_id} from Redis: {e}",
                exc_info=True,
            )
            return None

    async def get_notifications_for_recipient(
        self,
        recipient: str,
    ) -> list[NotificationRecord]:
        history_key = self.RECIPIENT_HISTORY_KEY_PREFIX + recipient
        try:
            notification_ids_str = await self.redis_client.lrange(history_key, 0, -1)
            notification_ids = [UUID(nid) for nid in notification_ids_str]
            notifications = []
            for notification_id in notification_ids:
                notification = await self.get_notification_by_id(notification_id)
                if notification:
                    notifications.append(notification)
            self.logger.debug(
                f"Retrieved {len(notifications)} notifications for recipient {recipient}.",
            )
            return notifications
        except Exception as e:
            self.logger.error(
                f"Error getting notifications for recipient {recipient} from Redis: {e}",
                exc_info=True,
            )
            return []

    async def delete_notification(self, notification_id: UUID) -> bool:
        key = self.NOTIFICATION_KEY_PREFIX + str(notification_id)
        try:
            result = await self.redis_client.delete(key)
            if result > 0:
                self.logger.debug(f"Deleted notification {notification_id} from Redis.")
                return True
            self.logger.debug(
                f"Notification {notification_id} not found for deletion in Redis.",
            )
            return False
        except Exception as e:
            self.logger.error(
                f"Error deleting notification {notification_id} from Redis: {e}",
                exc_info=True,
            )
            return False
