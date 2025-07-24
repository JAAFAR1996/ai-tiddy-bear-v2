import smtplib
from typing import Any

import requests

from src.domain.interfaces.notification_clients import (
    IEmailClient,
    IInAppNotifier,
    IPushNotifier,
    ISMSClient,
)
from src.infrastructure.logging_config import get_logger

logger = get_logger(__name__, component="notification_clients")


class EmailClient(IEmailClient):
    """Production implementation of IEmailClient using SMTP."""

    def __init__(
        self, smtp_server: str, smtp_port: int, username: str, password: str
    ) -> None:
        self.logger = logger
        self.smtp_server = smtp_server
        self.smtp_port = smtp_port
        self.username = username
        self.password = password

    async def send_email(self, recipient: str, subject: str, body: str) -> bool:
        try:
            message = f"Subject: {subject}\n\n{body}"
            with smtplib.SMTP(self.smtp_server, self.smtp_port) as server:
                server.starttls()
                server.login(self.username, self.password)
                server.sendmail(self.username, recipient, message)
            self.logger.info(f"Email sent to {recipient} with subject: {subject}")
            return True
        except Exception:
            self.logger.exception(f"Failed to send email to {recipient}")
            return False


class SMSClient(ISMSClient):
    """Production implementation of ISMSClient using external SMS API."""

    def __init__(self, api_url: str, api_key: str) -> None:
        self.logger = logger
        self.api_url = api_url
        self.api_key = api_key

    async def send_sms(self, recipient_phone_number: str, message: str) -> bool:
        try:
            payload = {
                "to": recipient_phone_number,
                "message": message,
                "api_key": self.api_key,
            }
            response = requests.post(self.api_url, json=payload, timeout=10)
            response.raise_for_status()
            self.logger.info(f"SMS sent to {recipient_phone_number}")
            return True
        except Exception:
            self.logger.exception(f"Failed to send SMS to {recipient_phone_number}")
            return False


class InAppNotifier(IInAppNotifier):
    """Production implementation of IInAppNotifier using internal notification system."""

    def __init__(self, notification_service_url: str) -> None:
        self.logger = logger
        self.notification_service_url = notification_service_url

    async def send_in_app_notification(
        self,
        recipient_user_id: str,
        message: str,
        metadata: dict[str, Any],
    ) -> bool:
        try:
            payload = {
                "user_id": recipient_user_id,
                "message": message,
                "metadata": metadata,
            }
            response = requests.post(
                self.notification_service_url, json=payload, timeout=10
            )
            response.raise_for_status()
            self.logger.info(f"In-app notification sent to {recipient_user_id}")
            return True
        except Exception:
            self.logger.exception(
                f"Failed to send in-app notification to {recipient_user_id}"
            )
            return False


class PushNotifier(IPushNotifier):
    """Production implementation of IPushNotifier using push notification service (e.g., FCM)."""

    def __init__(self, push_service_url: str, api_key: str) -> None:
        self.logger = logger
        self.push_service_url = push_service_url
        self.api_key = api_key

    async def send_push_notification(
        self,
        device_token: str,
        title: str,
        body: str,
        metadata: dict[str, Any],
    ) -> bool:
        try:
            payload = {
                "to": device_token,
                "title": title,
                "body": body,
                "metadata": metadata,
                "api_key": self.api_key,
            }
            response = requests.post(self.push_service_url, json=payload, timeout=10)
            response.raise_for_status()
            self.logger.info(f"Push notification sent to device {device_token}")
            return True
        except Exception:
            self.logger.exception(
                f"Failed to send push notification to device {device_token}"
            )
            return False
