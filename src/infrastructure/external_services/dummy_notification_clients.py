from typing import Any

from src.domain.interfaces.notification_clients import (
    IEmailClient,
    IInAppNotifier,
    IPushNotifier,
    ISMSClient,
)
from src.infrastructure.logging_config import get_logger

logger = get_logger(__name__, component="dummy_notification_clients")


class DummyEmailClient(IEmailClient):
    """Dummy implementation of IEmailClient for simulation purposes."""

    async def send_email(self, recipient: str, subject: str, body: str) -> bool:
        self.logger.info(
            f"[DUMMY EMAIL] Sending email to {recipient} with subject: {subject}",
        )
        return True

    def __init__(self) -> None:
        self.logger = logger


class DummySMSClient(ISMSClient):
    """Dummy implementation of ISMSClient for simulation purposes."""

    async def send_sms(self, recipient_phone_number: str, message: str) -> bool:
        self.logger.info(
            f"[DUMMY SMS] Sending SMS to {recipient_phone_number}: {message}",
        )
        return True

    def __init__(self) -> None:
        self.logger = logger


class DummyInAppNotifier(IInAppNotifier):
    """Dummy implementation of IInAppNotifier for simulation purposes."""

    async def send_in_app_notification(
        self,
        recipient_user_id: str,
        message: str,
        metadata: dict[str, Any],
    ) -> bool:
        self.logger.info(
            f"[DUMMY IN-APP] Sending in-app notification to {recipient_user_id}: {message} (Metadata: {metadata})",
        )
        return True

    def __init__(self) -> None:
        self.logger = logger


class DummyPushNotifier(IPushNotifier):
    """Dummy implementation of IPushNotifier for simulation purposes."""

    async def send_push_notification(
        self,
        device_token: str,
        title: str,
        body: str,
        metadata: dict[str, Any],
    ) -> bool:
        self.logger.info(
            f"[DUMMY PUSH] Sending push notification to device {device_token} - Title: {title}, Body: {body} (Metadata: {metadata})",
        )
        return True

    def __init__(self) -> None:
        self.logger = logger
