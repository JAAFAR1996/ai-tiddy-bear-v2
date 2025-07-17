from abc import ABC, abstractmethod


class IEmailClient(ABC):
    """Abstract interface for sending emails."""

    @abstractmethod
    async def send_email(self, recipient: str, subject: str, body: str) -> bool: ...


class ISMSClient(ABC):
    """Abstract interface for sending SMS messages."""

    @abstractmethod
    async def send_sms(self, recipient_phone_number: str, message: str) -> bool: ...


class IInAppNotifier(ABC):
    """Abstract interface for sending in-app notifications."""

    @abstractmethod
    async def send_in_app_notification(
        self,
        recipient_user_id: str,
        message: str,
        metadata: dict,
    ) -> bool: ...


class IPushNotifier(ABC):
    """Abstract interface for sending push notifications."""

    @abstractmethod
    async def send_push_notification(
        self,
        device_token: str,
        title: str,
        body: str,
        metadata: dict,
    ) -> bool: ...
