"""Provides services for sending various types of notifications.

This service handles sending notifications to parents and system alerts
through different channels such as email, SMS, in-app, and push notifications.
It manages notification queues and history, ensuring timely and reliable
delivery of important information.
"""

import logging
from datetime import UTC, datetime
from enum import Enum
from typing import Any
from uuid import uuid4

from src.application.interfaces.safety_monitor import SafetyMonitor
from src.common.exceptions import ServiceUnavailableError
from src.domain.interfaces.notification_clients import (
    IEmailClient,
    IInAppNotifier,
    IPushNotifier,
    ISMSClient,
)
from src.domain.interfaces.notification_repository import INotificationRepository
from src.domain.value_objects.notification import NotificationRecord, NotificationStatus
from src.domain.value_objects.safety_level import SafetyLevel
from src.infrastructure.config.services.notification_config import NotificationConfig
from src.infrastructure.logging_config import get_logger

logger = get_logger(__name__, component="notification_service")


class NotificationType(Enum):
    """Enumeration for different types of notifications."""

    SAFETY_ALERT = "safety_alert"
    PARENT_UPDATE = "parent_update"
    SYSTEM_INFO = "system_info"
    INTERACTION_SUMMARY = "interaction_summary"


class NotificationChannel(Enum):
    """Enumeration for different notification channels."""

    EMAIL = "email"
    SMS = "sms"
    IN_APP = "in_app"
    PUSH = "push"


class NotificationService:
    """Service for handling various types of notifications to parents and system alerts."""

    def __init__(
        self,
        config: NotificationConfig,
        repository: INotificationRepository,
        email_client: IEmailClient,
        sms_client: ISMSClient,
        in_app_notifier: IInAppNotifier,
        push_notifier: IPushNotifier,
        logger: logging.Logger = logger,
        safety_monitor: SafetyMonitor = None,
    ) -> None:
        """Initializes the notification service with configuration, repository, and external clients.

        Args:
            config: Configuration for notification settings.
            repository: The repository for storing and retrieving notification records.
            email_client: Client for sending email notifications.
            sms_client: Client for sending SMS notifications.
            in_app_notifier: Notifier for sending in-app messages.
            push_notifier: Notifier for sending push notifications.
            logger: Logger instance for logging service operations.
            safety_monitor: Optional SafetyMonitor for content validation.

        """
        self.config = config
        self.repository = repository
        self.email_client = email_client
        self.sms_client = sms_client
        self.in_app_notifier = in_app_notifier
        self.push_notifier = push_notifier
        self.logger = logger
        self.safety_monitor = safety_monitor

    async def send_notification(
        self,
        recipient: str,
        message: str,
        notification_type: NotificationType = NotificationType.SYSTEM_INFO,
        channel: NotificationChannel = NotificationChannel.IN_APP,
        urgent: bool = False,
    ) -> dict[str, Any]:
        """Sends a notification to a recipient.

        Args:
            recipient: The recipient of the notification (e.g., parent ID, email).
            message: The content of the notification.
            notification_type: The type of notification.
            channel: The channel through which to send the notification.
            urgent: Whether the notification is urgent.

        Returns:
            A dictionary representing the sent notification's status.

        """
        try:
            if self.safety_monitor:
                safety_result = await self.safety_monitor.check_content_safety(message)
                if safety_result.risk_level in [
                    SafetyLevel.UNSAFE,
                    SafetyLevel.POTENTIALLY_UNSAFE,
                ]:
                    self.logger.warning(
                        "Notification blocked: Unsafe content detected for recipient "
                        f"{recipient}. Message: '{message[:50]}...' Reason: "
                        f"{safety_result.analysis_details}",
                    )
                    return {
                        "id": None,
                        "status": NotificationStatus.BLOCKED.value,
                        "message": (
                            "Notification content blocked due to safety concerns."
                        ),
                    }

            notification_id = uuid4()
            max_attempts = (
                self.config.urgent_max_attempts
                if urgent
                else self.config.default_max_attempts
            )

            notification_record = NotificationRecord(
                id=notification_id,
                recipient=recipient,
                message=message,
                notification_type=notification_type.value,
                channel=channel.value,
                urgent=urgent,
                created_at=datetime.now(UTC),
                status=NotificationStatus.PENDING,
                attempts=0,
                max_attempts=max_attempts,
            )
            await self.repository.save_notification(notification_record)
            self.logger.info(
                f"Notification {notification_id} queued for {recipient} via {channel.value}.",
            )

            # Send based on channel
            success = await self._send_by_channel(notification_record)

            notification_record.attempts += 1
            notification_record.last_attempt_at = datetime.now(UTC)
            notification_record.status = (
                NotificationStatus.SENT if success else NotificationStatus.FAILED
            )
            notification_record.error_message = (
                None if success else "Failed to send via channel"
            )

            await self.repository.save_notification(notification_record)
            self.logger.info(
                f"Notification {notification_id} sent to {recipient} via {channel.value} with status {notification_record.status.value}."
            )
            return {
                "id": str(notification_id),
                "status": notification_record.status.value,
                "message": "Notification process initiated.",
            }
        except (
            ServiceUnavailableError,
            ConnectionError,
            TimeoutError,
            ValueError,
        ) as e:
            self.logger.error(
                f"Specific error sending notification: {e}",
                exc_info=True,
            )
            return {
                "id": str(notification_id),
                "status": NotificationStatus.FAILED.value,
                "message": f"Failed to send notification: {e}",
            }
        except Exception as e:
            self.logger.critical(
                f"Unexpected critical error sending notification: {e}",
                exc_info=True,
            )
            return {
                "id": str(notification_id),
                "status": NotificationStatus.FAILED.value,
                "message": (
                    "An unexpected critical error occurred during notification sending."
                ),
            }

    async def _send_by_channel(self, notification: NotificationRecord) -> bool:
        """Sends a notification through the specified channel using the appropriate client.

        Args:
            notification: The notification record.

        Returns:
            True if sending was successful, False otherwise.

        """
        channel = notification.channel
        message = notification.message
        recipient = notification.recipient
        notification_id = notification.id

        try:
            if channel == NotificationChannel.EMAIL.value:
                # Assuming recipient is an email address for email notifications
                return await self.email_client.send_email(
                    recipient,
                    f"AI Teddy Bear Notification: {notification.notification_type}",
                    message,
                )
            if channel == NotificationChannel.SMS.value:
                # Assuming recipient is a phone number for SMS notifications
                return await self.sms_client.send_sms(recipient, message)
            if channel == NotificationChannel.IN_APP.value:
                # Assuming recipient is a user ID for in-app notifications
                return await self.in_app_notifier.send_in_app_notification(
                    recipient,
                    message,
                    {"notification_id": str(notification_id)},
                )
            if channel == NotificationChannel.PUSH.value:
                # Assuming recipient is a device token or user ID for push notifications
                # For simplicity, using recipient as device_token here.
                return await self.push_notifier.send_push_notification(
                    recipient,
                    (
                        "AI Teddy Bear: "
                        f"{notification.notification_type.replace('_', ' ').title()}"
                    ),
                    message,
                    {"notification_id": str(notification_id)},
                )
            self.logger.warning(
                f"Notification {notification_id}: Unknown notification channel: {channel}",
            )
            return False
        except Exception as e:
            self.logger.error(
                f"Notification {notification_id}: Failed to send via {channel} "
                f"to {recipient}: {e}",
                exc_info=True,
            )
            return False

    async def get_notification_history(
        self,
        recipient: str,
    ) -> list[NotificationRecord]:
        """Retrieves the notification history for a specific recipient from the repository.

        Args:
            recipient: The recipient's identifier.

        Returns:
            A list of NotificationRecord objects.

        """
        self.logger.debug(f"Retrieving notification history for recipient: {recipient}")
        history = await self.repository.get_notifications_for_recipient(recipient)
        self.logger.info(
            f"Retrieved {len(history)} notifications for recipient: {recipient}",
        )
        return history
