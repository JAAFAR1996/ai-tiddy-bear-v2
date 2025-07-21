"""Tests for Notification Service
Testing notification management and delivery functionality.
"""

from datetime import datetime
from unittest.mock import patch

import pytest

from src.application.services.notification_service import (
    NotificationChannel,
    NotificationService,
    NotificationType,
)


class TestNotificationService:
    """Test the Notification Service."""

    @pytest.fixture
    def service(self):
        """Create a notification service instance."""
        return NotificationService()

    def test_initialization(self, service):
        """Test service initialization."""
        assert isinstance(service, NotificationService)
        assert hasattr(service, "notification_queue")
        assert hasattr(service, "notification_history")
        assert isinstance(service.notification_queue, list)
        assert isinstance(service.notification_history, dict)
        assert len(service.notification_queue) == 0
        assert len(service.notification_history) == 0

    def test_notification_type_enum(self):
        """Test NotificationType enum values."""
        assert NotificationType.SAFETY_ALERT == "safety_alert"
        assert NotificationType.PARENT_UPDATE == "parent_update"
        assert NotificationType.SYSTEM_INFO == "system_info"
        assert NotificationType.INTERACTION_SUMMARY == "interaction_summary"

    def test_notification_channel_enum(self):
        """Test NotificationChannel enum values."""
        assert NotificationChannel.EMAIL == "email"
        assert NotificationChannel.SMS == "sms"
        assert NotificationChannel.IN_APP == "in_app"
        assert NotificationChannel.PUSH == "push"

    @pytest.mark.asyncio
    async def test_send_notification_basic(self, service):
        """Test basic notification sending."""
        recipient = "parent_123"
        message = "Your child has completed their learning session"

        with patch(
            "src.application.services.notification_service.datetime"
        ) as mock_datetime:
            mock_datetime.now.return_value = datetime(2024, 1, 15, 10, 30, 0)

            result = await service.send_notification(recipient, message)

        assert result["recipient"] == recipient
        assert result["message"] == message
        assert result["type"] == NotificationType.SYSTEM_INFO.value
        assert result["channel"] == NotificationChannel.IN_APP.value
        assert result["urgent"] is False
        assert result["status"] == "sent"
        assert result["attempts"] == 0
        assert result["max_attempts"] == 1

        # Check history was updated
        assert len(service.notification_history[recipient]) == 1
        assert service.notification_history[recipient][0] == result

    @pytest.mark.asyncio
    async def test_send_notification_urgent(self, service):
        """Test sending urgent notification."""
        recipient = "parent_456"
        message = "Safety alert: Inappropriate content detected"

        result = await service.send_notification(
            recipient=recipient,
            message=message,
            notification_type=NotificationType.SAFETY_ALERT,
            channel=NotificationChannel.EMAIL,
            urgent=True,
        )

        assert result["type"] == NotificationType.SAFETY_ALERT.value
        assert result["channel"] == NotificationChannel.EMAIL.value
        assert result["urgent"] is True
        # Urgent notifications get more attempts
        assert result["max_attempts"] == 3
        assert result["status"] == "sent"

    @pytest.mark.asyncio
    async def test_send_notification_all_channels(self, service):
        """Test sending notifications through all channels."""
        recipient = "parent_789"
        message = "Test notification"
        channels = [
            NotificationChannel.EMAIL,
            NotificationChannel.SMS,
            NotificationChannel.IN_APP,
            NotificationChannel.PUSH,
        ]

        for channel in channels:
            result = await service.send_notification(
                recipient=recipient, message=message, channel=channel
            )

            assert result["channel"] == channel.value
            assert result["status"] == "sent"

    @pytest.mark.asyncio
    async def test_send_notification_all_types(self, service):
        """Test sending all notification types."""
        recipient = "parent_test"
        message = "Test message"
        types = [
            NotificationType.SAFETY_ALERT,
            NotificationType.PARENT_UPDATE,
            NotificationType.SYSTEM_INFO,
            NotificationType.INTERACTION_SUMMARY,
        ]

        for notification_type in types:
            result = await service.send_notification(
                recipient=recipient,
                message=message,
                notification_type=notification_type,
            )

            assert result["type"] == notification_type.value
            assert result["status"] == "sent"

    @pytest.mark.asyncio
    async def test_send_notification_id_generation(self, service):
        """Test notification ID generation."""
        recipient = "parent_id_test"
        message = "ID generation test"

        with patch(
            "src.application.services.notification_service.datetime"
        ) as mock_datetime:
            mock_datetime.now.return_value = datetime(2024, 1, 15, 10, 30, 0)
            mock_datetime.now().timestamp.return_value = 1705312200.0

            result = await service.send_notification(recipient, message)

        assert "notif_" in result["id"]
        assert result["id"] != ""

    @pytest.mark.asyncio
    async def test_send_by_channel_email(self, service):
        """Test sending by email channel."""
        notification = {
            "channel": NotificationChannel.EMAIL.value,
            "message": "Test email message",
            "recipient": "test@example.com",
        }

        with patch(
            "src.application.services.notification_service.logger"
        ) as mock_logger:
            result = await service._send_by_channel(notification)

            assert result is True
            mock_logger.info.assert_called_once()
            log_call = mock_logger.info.call_args[0][0]
            assert "Simulating email send" in log_call
            assert "test@example.com" in log_call

    @pytest.mark.asyncio
    async def test_send_by_channel_sms(self, service):
        """Test sending by SMS channel."""
        notification = {
            "channel": NotificationChannel.SMS.value,
            "message": "Test SMS message",
            "recipient": "+1234567890",
        }

        with patch(
            "src.application.services.notification_service.logger"
        ) as mock_logger:
            result = await service._send_by_channel(notification)

            assert result is True
            mock_logger.info.assert_called_once()
            log_call = mock_logger.info.call_args[0][0]
            assert "Simulating SMS send" in log_call
            assert "+1234567890" in log_call

    @pytest.mark.asyncio
    async def test_send_by_channel_in_app(self, service):
        """Test sending by in-app channel."""
        notification = {
            "channel": NotificationChannel.IN_APP.value,
            "message": "Test in-app message",
            "recipient": "user_123",
        }

        with patch(
            "src.application.services.notification_service.logger"
        ) as mock_logger:
            result = await service._send_by_channel(notification)

            assert result is True
            mock_logger.info.assert_called_once()
            log_call = mock_logger.info.call_args[0][0]
            assert "Simulating in-app notification" in log_call
            assert "user_123" in log_call

    @pytest.mark.asyncio
    async def test_send_by_channel_push(self, service):
        """Test sending by push channel."""
        notification = {
            "channel": NotificationChannel.PUSH.value,
            "message": "Test push message",
            "recipient": "device_token_123",
        }

        with patch(
            "src.application.services.notification_service.logger"
        ) as mock_logger:
            result = await service._send_by_channel(notification)

            assert result is True
            mock_logger.info.assert_called_once()
            log_call = mock_logger.info.call_args[0][0]
            assert "Simulating push notification" in log_call
            assert "device_token_123" in log_call

    @pytest.mark.asyncio
    async def test_send_by_channel_unknown(self, service):
        """Test sending by unknown channel."""
        notification = {
            "channel": "unknown_channel",
            "message": "Test message",
            "recipient": "recipient",
        }

        with patch(
            "src.application.services.notification_service.logger"
        ) as mock_logger:
            result = await service._send_by_channel(notification)

            assert result is False
            mock_logger.warning.assert_called_once()
            log_call = mock_logger.warning.call_args[0][0]
            assert "Unknown notification channel" in log_call

    def test_get_notification_history_empty(self, service):
        """Test getting notification history for recipient with no history."""
        history = service.get_notification_history("nonexistent_recipient")

        assert history == []

    def test_get_notification_history_with_notifications(self, service):
        """Test getting notification history for recipient with notifications."""
        recipient = "test_recipient"

        # Manually add notifications to history
        notifications = [
            {"id": "notif_1", "message": "Message 1", "recipient": recipient},
            {"id": "notif_2", "message": "Message 2", "recipient": recipient},
        ]

        service.notification_history[recipient] = notifications

        history = service.get_notification_history(recipient)

        assert len(history) == 2
        assert history == notifications

    @pytest.mark.asyncio
    async def test_multiple_notifications_same_recipient(self, service):
        """Test sending multiple notifications to the same recipient."""
        recipient = "parent_multiple"
        messages = [
            "First notification",
            "Second notification",
            "Third notification",
        ]

        for message in messages:
            await service.send_notification(recipient, message)

        history = service.get_notification_history(recipient)
        assert len(history) == 3

        for i, notification in enumerate(history):
            assert notification["message"] == messages[i]
            assert notification["recipient"] == recipient

    @pytest.mark.asyncio
    async def test_multiple_recipients_isolation(self, service):
        """Test that notifications for different recipients are properly isolated."""
        recipients = ["parent_a", "parent_b", "parent_c"]

        for i, recipient in enumerate(recipients):
            await service.send_notification(recipient, f"Message for {recipient}")

        # Each recipient should have exactly one notification
        for recipient in recipients:
            history = service.get_notification_history(recipient)
            assert len(history) == 1
            assert history[0]["recipient"] == recipient
            assert recipient in history[0]["message"]

    @pytest.mark.asyncio
    async def test_notification_error_handling(self, service):
        """Test error handling in notification sending."""
        recipient = "error_test"
        message = "Error test message"

        # Mock an exception in _send_by_channel
        with patch.object(
            service, "_send_by_channel", side_effect=Exception("Channel error")
        ):
            with patch(
                "src.application.services.notification_service.logger"
            ) as mock_logger:
                result = await service.send_notification(recipient, message)

                assert result["id"] == ""
                assert result["status"] == "error"
                assert "Channel error" in result["message"]

                mock_logger.error.assert_called_once()
                error_log = mock_logger.error.call_args[0][0]
                assert "Error sending notification" in error_log

    @pytest.mark.asyncio
    async def test_concurrent_notifications(self, service):
        """Test concurrent notification sending."""
        import asyncio

        recipients = [f"parent_{i}" for i in range(5)]
        messages = [f"Message {i}" for i in range(5)]

        # Send all notifications concurrently
        tasks = [
            service.send_notification(recipient, message)
            for recipient, message in zip(recipients, messages, strict=False)
        ]

        results = await asyncio.gather(*tasks)

        # All should succeed
        assert len(results) == 5
        assert all(r["status"] == "sent" for r in results)

        # Each recipient should have their notification
        for i, recipient in enumerate(recipients):
            history = service.get_notification_history(recipient)
            assert len(history) == 1
            assert history[0]["message"] == messages[i]

    @pytest.mark.asyncio
    async def test_notification_timestamp_consistency(self, service):
        """Test that notification timestamps are properly set."""
        recipient = "timestamp_test"
        message = "Timestamp test message"

        with patch(
            "src.application.services.notification_service.datetime"
        ) as mock_datetime:
            fixed_time = datetime(2024, 3, 15, 14, 30, 45)
            mock_datetime.now.return_value = fixed_time

            result = await service.send_notification(recipient, message)

        assert result["created_at"] == fixed_time

        # Check that timestamp is stored in history
        history = service.get_notification_history(recipient)
        assert history[0]["created_at"] == fixed_time

    @pytest.mark.asyncio
    async def test_notification_workflow_realistic(self, service):
        """Test a realistic notification workflow."""
        parent_id = "parent_realistic"

        # Send initial system info
        result1 = await service.send_notification(
            recipient=parent_id,
            message="Your child started a new session",
            notification_type=NotificationType.SYSTEM_INFO,
        )
        assert result1["status"] == "sent"

        # Send interaction summary
        result2 = await service.send_notification(
            recipient=parent_id,
            message="Daily interaction summary: 3 stories, 2 games",
            notification_type=NotificationType.INTERACTION_SUMMARY,
            channel=NotificationChannel.EMAIL,
        )
        assert result2["status"] == "sent"

        # Send urgent safety alert
        result3 = await service.send_notification(
            recipient=parent_id,
            message="Safety review required for recent interaction",
            notification_type=NotificationType.SAFETY_ALERT,
            channel=NotificationChannel.SMS,
            urgent=True,
        )
        assert result3["status"] == "sent"

        # Check history
        history = service.get_notification_history(parent_id)
        assert len(history) == 3

        # Verify order and content
        assert history[0]["type"] == NotificationType.SYSTEM_INFO.value
        assert history[1]["type"] == NotificationType.INTERACTION_SUMMARY.value
        assert history[2]["type"] == NotificationType.SAFETY_ALERT.value
        assert history[2]["urgent"] is True

    @pytest.mark.parametrize(
        "channel",
        [
            NotificationChannel.EMAIL,
            NotificationChannel.SMS,
            NotificationChannel.IN_APP,
            NotificationChannel.PUSH,
        ],
    )
    @pytest.mark.asyncio
    async def test_all_channels_send_successfully(self, service, channel):
        """Test that all channels can send notifications successfully."""
        recipient = f"test_{channel.value}_recipient"
        message = f"Test message for {channel.value}"

        result = await service.send_notification(
            recipient=recipient, message=message, channel=channel
        )

        assert result["status"] == "sent"
        assert result["channel"] == channel.value
        assert result["recipient"] == recipient
        assert result["message"] == message

    @pytest.mark.asyncio
    async def test_edge_cases_empty_values(self, service):
        """Test edge cases with empty or None values."""
        # Empty recipient
        result = await service.send_notification("", "test message")
        assert result["status"] == "sent"  # Should still work
        assert result["recipient"] == ""

        # Empty message
        result = await service.send_notification("test_recipient", "")
        assert result["status"] == "sent"  # Should still work
        assert result["message"] == ""

    @pytest.mark.asyncio
    async def test_notification_max_attempts_configuration(self, service):
        """Test that max attempts are configured correctly."""
        recipient = "attempts_test"
        message = "Attempts test"

        # Non-urgent notification
        result1 = await service.send_notification(recipient, message, urgent=False)
        assert result1["max_attempts"] == 1

        # Urgent notification
        result2 = await service.send_notification(recipient, message, urgent=True)
        assert result2["max_attempts"] == 3

    def test_service_state_isolation(self):
        """Test that different service instances maintain separate state."""
        service1 = NotificationService()
        service2 = NotificationService()

        # Each should start with empty state
        assert len(service1.notification_queue) == 0
        assert len(service2.notification_queue) == 0
        assert len(service1.notification_history) == 0
        assert len(service2.notification_history) == 0

        # Add to first service
        service1.notification_history["test"] = [{"id": "test_notif"}]

        # Second service should be unaffected
        assert len(service1.notification_history) == 1
        assert len(service2.notification_history) == 0
