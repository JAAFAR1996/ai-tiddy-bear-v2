"""Comprehensive test suite for application/interfaces/infrastructure_services.py

This test file validates all infrastructure service interfaces including
encryption, data retention, parent verification, audit logging, access control,
content filtering, email services, settings, and event bus functionality.
"""

from abc import ABC
from typing import Any

import pytest

from src.application.interfaces.infrastructure_services import (
    IAccessControlService,
    IAuditLogger,
    IContentFilterService,
    IDataRetentionService,
    IEmailService,
    IEventBus,
    IParentVerificationService,
    ISettingsProvider,
)
from src.domain.interfaces.security_interfaces import IEncryptionService


class MockEncryptionService(IEncryptionService):
    """Mock implementation of IEncryptionService for testing."""

    def __init__(self):
        self.encrypt_called = False
        self.decrypt_called = False
        self.rotate_keys_called = False
        self.encrypted_data = {}
        self.key_rotation_success = True

    async def encrypt_child_data(self, data: str) -> str:
        self.encrypt_called = True
        encrypted = f"encrypted_{data}"
        self.encrypted_data[encrypted] = data
        return encrypted

    async def decrypt_child_data(self, encrypted_data: str) -> str:
        self.decrypt_called = True
        return self.encrypted_data.get(encrypted_data, "decrypted_data")

    async def rotate_keys(self) -> bool:
        self.rotate_keys_called = True
        return self.key_rotation_success


class MockDataRetentionService(IDataRetentionService):
    """Mock implementation of IDataRetentionService for testing."""

    def __init__(self):
        self.schedule_deletion_called = False
        self.export_child_data_called = False
        self.delete_expired_data_called = False
        self.scheduled_deletions = {}
        self.exported_data = {}
        self.deleted_ids = []

    async def schedule_deletion(self, child_id: str, retention_days: int) -> None:
        self.schedule_deletion_called = True
        self.scheduled_deletions[child_id] = retention_days

    async def export_child_data(self, child_id: str) -> str:
        self.export_child_data_called = True
        export_data = f"exported_data_for_{child_id}"
        self.exported_data[child_id] = export_data
        return export_data

    async def delete_expired_data(self) -> list[str]:
        self.delete_expired_data_called = True
        return self.deleted_ids


class MockParentVerificationService(IParentVerificationService):
    """Mock implementation of IParentVerificationService for testing."""

    def __init__(self):
        self.verify_parent_identity_called = False
        self.get_verification_methods_called = False
        self.verification_result = True
        self.verification_methods = ["email", "phone", "id_document"]

    async def verify_parent_identity(
        self,
        parent_id: str,
        verification_method: str,
        verification_data: dict[str, Any],
    ) -> bool:
        self.verify_parent_identity_called = True
        self.last_verification = {
            "parent_id": parent_id,
            "method": verification_method,
            "data": verification_data,
        }
        return self.verification_result

    async def get_verification_methods(self) -> list[str]:
        self.get_verification_methods_called = True
        return self.verification_methods


class MockAuditLogger(IAuditLogger):
    """Mock implementation of IAuditLogger for testing."""

    def __init__(self):
        self.log_child_access_called = False
        self.log_consent_change_called = False
        self.logged_access_events = []
        self.logged_consent_events = []

    async def log_child_access(
        self,
        parent_id: str,
        child_id: str,
        action: str,
        ip_address: str,
        success: bool,
    ) -> None:
        self.log_child_access_called = True
        self.logged_access_events.append(
            {
                "parent_id": parent_id,
                "child_id": child_id,
                "action": action,
                "ip_address": ip_address,
                "success": success,
            }
        )

    async def log_consent_change(
        self,
        parent_id: str,
        child_id: str,
        consent_type: str,
        action: str,
        metadata: dict[str, Any],
    ) -> None:
        self.log_consent_change_called = True
        self.logged_consent_events.append(
            {
                "parent_id": parent_id,
                "child_id": child_id,
                "consent_type": consent_type,
                "action": action,
                "metadata": metadata,
            }
        )


class MockAccessControlService(IAccessControlService):
    """Mock implementation of IAccessControlService for testing."""

    def __init__(self):
        self.verify_parent_child_access_called = False
        self.get_parent_children_called = False
        self.access_result = True
        self.parent_children = {}

    async def verify_parent_child_access(
        self, parent_id: str, child_id: str, operation: str
    ) -> bool:
        self.verify_parent_child_access_called = True
        self.last_access_check = {
            "parent_id": parent_id,
            "child_id": child_id,
            "operation": operation,
        }
        return self.access_result

    async def get_parent_children(self, parent_id: str) -> list[str]:
        self.get_parent_children_called = True
        return self.parent_children.get(parent_id, [])


class MockContentFilterService(IContentFilterService):
    """Mock implementation of IContentFilterService for testing."""

    def __init__(self):
        self.filter_content_called = False
        self.validate_topic_called = False
        self.filter_result = {
            "is_safe": True,
            "filtered_content": "safe content",
        }
        self.topic_validation_result = True

    async def filter_content(
        self, content: str, child_age: int, context: str = "general"
    ) -> dict[str, Any]:
        self.filter_content_called = True
        self.last_filter_request = {
            "content": content,
            "child_age": child_age,
            "context": context,
        }
        return self.filter_result

    async def validate_topic(self, topic: str, child_id: str) -> bool:
        self.validate_topic_called = True
        self.last_topic_validation = {"topic": topic, "child_id": child_id}
        return self.topic_validation_result


class MockEmailService(IEmailService):
    """Mock implementation of IEmailService for testing."""

    def __init__(self):
        self.send_email_called = False
        self.send_deletion_warning_called = False
        self.email_success = True
        self.sent_emails = []

    async def send_email(
        self, to: str, subject: str, template: str, context: dict[str, Any]
    ) -> bool:
        self.send_email_called = True
        self.sent_emails.append(
            {
                "to": to,
                "subject": subject,
                "template": template,
                "context": context,
            }
        )
        return self.email_success

    async def send_deletion_warning(
        self,
        parent_email: str,
        child_name: str,
        deletion_date: str,
        export_url: str,
    ) -> bool:
        self.send_deletion_warning_called = True
        self.sent_emails.append(
            {
                "type": "deletion_warning",
                "parent_email": parent_email,
                "child_name": child_name,
                "deletion_date": deletion_date,
                "export_url": export_url,
            }
        )
        return self.email_success


class MockSettingsProvider(ISettingsProvider):
    """Mock implementation of ISettingsProvider for testing."""

    def __init__(self):
        self.get_database_url_called = False
        self.get_encryption_key_called = False
        self.get_coppa_settings_called = False
        self.is_production_called = False
        self.database_url = "postgresql://test:test@localhost/test"
        self.encryption_key = "test_encryption_key"
        self.coppa_settings = {"retention_days": 90, "verify_parent": True}
        self.production_mode = False

    def get_database_url(self) -> str:
        self.get_database_url_called = True
        return self.database_url

    def get_encryption_key(self) -> str:
        self.get_encryption_key_called = True
        return self.encryption_key

    def get_coppa_settings(self) -> dict[str, Any]:
        self.get_coppa_settings_called = True
        return self.coppa_settings

    def is_production(self) -> bool:
        self.is_production_called = True
        return self.production_mode


class MockEventBus(IEventBus):
    """Mock implementation of IEventBus for testing."""

    def __init__(self):
        self.publish_event_called = False
        self.subscribe_to_events_called = False
        self.published_events = []
        self.subscriptions = {}

    async def publish_event(self, event_name: str, data: dict[str, Any]) -> None:
        self.publish_event_called = True
        self.published_events.append({"event_name": event_name, "data": data})

    async def subscribe_to_events(self, event_names: list[str], handler) -> None:
        self.subscribe_to_events_called = True
        for event_name in event_names:
            if event_name not in self.subscriptions:
                self.subscriptions[event_name] = []
            self.subscriptions[event_name].append(handler)


class TestInfrastructureServiceInterfaces:
    """Test suite for infrastructure service interfaces."""

    def test_all_interfaces_are_abstract(self):
        """Test that all service interfaces are abstract base classes."""
        interfaces = [
            IEncryptionService,
            IDataRetentionService,
            IParentVerificationService,
            IAuditLogger,
            IAccessControlService,
            IContentFilterService,
            IEmailService,
            ISettingsProvider,
            IEventBus,
        ]

        for interface in interfaces:
            assert issubclass(interface, ABC)
            assert interface.__abstractmethods__  # Has abstract methods

    def test_interfaces_cannot_be_instantiated(self):
        """Test that interfaces cannot be instantiated directly."""
        interfaces = [
            IEncryptionService,
            IDataRetentionService,
            IParentVerificationService,
            IAuditLogger,
            IAccessControlService,
            IContentFilterService,
            IEmailService,
            ISettingsProvider,
            IEventBus,
        ]

        for interface in interfaces:
            with pytest.raises(TypeError):
                interface()

    @pytest.mark.asyncio
    async def test_encryption_service_interface(self):
        """Test IEncryptionService interface implementation."""
        service = MockEncryptionService()

        # Test encrypt_child_data
        encrypted = await service.encrypt_child_data("test_data")
        assert service.encrypt_called
        assert encrypted == "encrypted_test_data"

        # Test decrypt_child_data
        decrypted = await service.decrypt_child_data(encrypted)
        assert service.decrypt_called
        assert decrypted == "test_data"

        # Test rotate_keys
        result = await service.rotate_keys()
        assert service.rotate_keys_called
        assert result is True

    @pytest.mark.asyncio
    async def test_data_retention_service_interface(self):
        """Test IDataRetentionService interface implementation."""
        service = MockDataRetentionService()

        # Test schedule_deletion
        await service.schedule_deletion("child_123", 90)
        assert service.schedule_deletion_called
        assert service.scheduled_deletions["child_123"] == 90

        # Test export_child_data
        export_data = await service.export_child_data("child_123")
        assert service.export_child_data_called
        assert export_data == "exported_data_for_child_123"

        # Test delete_expired_data
        service.deleted_ids = ["child_456", "child_789"]
        deleted = await service.delete_expired_data()
        assert service.delete_expired_data_called
        assert deleted == ["child_456", "child_789"]

    @pytest.mark.asyncio
    async def test_parent_verification_service_interface(self):
        """Test IParentVerificationService interface implementation."""
        service = MockParentVerificationService()

        # Test verify_parent_identity
        verification_data = {
            "email": "parent@example.com",
            "phone": "123-456-7890",
        }
        result = await service.verify_parent_identity(
            "parent_123", "email", verification_data
        )
        assert service.verify_parent_identity_called
        assert result is True
        assert service.last_verification["parent_id"] == "parent_123"
        assert service.last_verification["method"] == "email"
        assert service.last_verification["data"] == verification_data

        # Test get_verification_methods
        methods = await service.get_verification_methods()
        assert service.get_verification_methods_called
        assert methods == ["email", "phone", "id_document"]

    @pytest.mark.asyncio
    async def test_audit_logger_interface(self):
        """Test IAuditLogger interface implementation."""
        logger = MockAuditLogger()

        # Test log_child_access
        await logger.log_child_access(
            "parent_123", "child_456", "view_profile", "192.168.1.1", True
        )
        assert logger.log_child_access_called
        assert len(logger.logged_access_events) == 1
        access_event = logger.logged_access_events[0]
        assert access_event["parent_id"] == "parent_123"
        assert access_event["child_id"] == "child_456"
        assert access_event["action"] == "view_profile"
        assert access_event["ip_address"] == "192.168.1.1"
        assert access_event["success"] is True

        # Test log_consent_change
        metadata = {"previous_consent": False, "new_consent": True}
        await logger.log_consent_change(
            "parent_123", "child_456", "data_collection", "granted", metadata
        )
        assert logger.log_consent_change_called
        assert len(logger.logged_consent_events) == 1
        consent_event = logger.logged_consent_events[0]
        assert consent_event["parent_id"] == "parent_123"
        assert consent_event["child_id"] == "child_456"
        assert consent_event["consent_type"] == "data_collection"
        assert consent_event["action"] == "granted"
        assert consent_event["metadata"] == metadata

    @pytest.mark.asyncio
    async def test_access_control_service_interface(self):
        """Test IAccessControlService interface implementation."""
        service = MockAccessControlService()

        # Test verify_parent_child_access
        result = await service.verify_parent_child_access(
            "parent_123", "child_456", "read"
        )
        assert service.verify_parent_child_access_called
        assert result is True
        assert service.last_access_check["parent_id"] == "parent_123"
        assert service.last_access_check["child_id"] == "child_456"
        assert service.last_access_check["operation"] == "read"

        # Test get_parent_children
        service.parent_children["parent_123"] = ["child_456", "child_789"]
        children = await service.get_parent_children("parent_123")
        assert service.get_parent_children_called
        assert children == ["child_456", "child_789"]

    @pytest.mark.asyncio
    async def test_content_filter_service_interface(self):
        """Test IContentFilterService interface implementation."""
        service = MockContentFilterService()

        # Test filter_content
        result = await service.filter_content("test content", 8, "conversation")
        assert service.filter_content_called
        assert result == {"is_safe": True, "filtered_content": "safe content"}
        assert service.last_filter_request["content"] == "test content"
        assert service.last_filter_request["child_age"] == 8
        assert service.last_filter_request["context"] == "conversation"

        # Test validate_topic
        result = await service.validate_topic("animals", "child_456")
        assert service.validate_topic_called
        assert result is True
        assert service.last_topic_validation["topic"] == "animals"
        assert service.last_topic_validation["child_id"] == "child_456"

    @pytest.mark.asyncio
    async def test_email_service_interface(self):
        """Test IEmailService interface implementation."""
        service = MockEmailService()

        # Test send_email
        context = {"child_name": "Alice", "parent_name": "Bob"}
        result = await service.send_email(
            "parent@example.com", "Test Subject", "welcome", context
        )
        assert service.send_email_called
        assert result is True
        assert len(service.sent_emails) == 1
        email = service.sent_emails[0]
        assert email["to"] == "parent@example.com"
        assert email["subject"] == "Test Subject"
        assert email["template"] == "welcome"
        assert email["context"] == context

        # Test send_deletion_warning
        result = await service.send_deletion_warning(
            "parent@example.com",
            "Alice",
            "2024-01-01",
            "https://example.com/export",
        )
        assert service.send_deletion_warning_called
        assert result is True
        assert len(service.sent_emails) == 2
        warning_email = service.sent_emails[1]
        assert warning_email["type"] == "deletion_warning"
        assert warning_email["parent_email"] == "parent@example.com"
        assert warning_email["child_name"] == "Alice"
        assert warning_email["deletion_date"] == "2024-01-01"
        assert warning_email["export_url"] == "https://example.com/export"

    def test_settings_provider_interface(self):
        """Test ISettingsProvider interface implementation."""
        provider = MockSettingsProvider()

        # Test get_database_url
        url = provider.get_database_url()
        assert provider.get_database_url_called
        assert url == "postgresql://test:test@localhost/test"

        # Test get_encryption_key
        key = provider.get_encryption_key()
        assert provider.get_encryption_key_called
        assert key == "test_encryption_key"

        # Test get_coppa_settings
        settings = provider.get_coppa_settings()
        assert provider.get_coppa_settings_called
        assert settings == {"retention_days": 90, "verify_parent": True}

        # Test is_production
        is_prod = provider.is_production()
        assert provider.is_production_called
        assert is_prod is False

    @pytest.mark.asyncio
    async def test_event_bus_interface(self):
        """Test IEventBus interface implementation."""
        bus = MockEventBus()

        # Test publish_event
        event_data = {"child_id": "child_123", "action": "profile_updated"}
        await bus.publish_event("child_profile_updated", event_data)
        assert bus.publish_event_called
        assert len(bus.published_events) == 1
        published_event = bus.published_events[0]
        assert published_event["event_name"] == "child_profile_updated"
        assert published_event["data"] == event_data

        # Test subscribe_to_events
        def handler(event):
            return None

        await bus.subscribe_to_events(["child_registered", "child_updated"], handler)
        assert bus.subscribe_to_events_called
        assert "child_registered" in bus.subscriptions
        assert "child_updated" in bus.subscriptions
        assert handler in bus.subscriptions["child_registered"]
        assert handler in bus.subscriptions["child_updated"]

    @pytest.mark.asyncio
    async def test_encryption_service_error_handling(self):
        """Test error handling in encryption service."""
        service = MockEncryptionService()
        service.key_rotation_success = False

        # Test failed key rotation
        result = await service.rotate_keys()
        assert result is False

    @pytest.mark.asyncio
    async def test_data_retention_service_empty_results(self):
        """Test data retention service with empty results."""
        service = MockDataRetentionService()
        service.deleted_ids = []

        # Test delete_expired_data with no expired data
        deleted = await service.delete_expired_data()
        assert deleted == []

    @pytest.mark.asyncio
    async def test_parent_verification_service_failure(self):
        """Test parent verification service failure."""
        service = MockParentVerificationService()
        service.verification_result = False

        # Test failed verification
        result = await service.verify_parent_identity(
            "parent_123", "email", {"email": "invalid"}
        )
        assert result is False

    @pytest.mark.asyncio
    async def test_access_control_service_denial(self):
        """Test access control service denial."""
        service = MockAccessControlService()
        service.access_result = False

        # Test access denied
        result = await service.verify_parent_child_access(
            "parent_123", "child_456", "delete"
        )
        assert result is False

    @pytest.mark.asyncio
    async def test_content_filter_service_unsafe_content(self):
        """Test content filter service with unsafe content."""
        service = MockContentFilterService()
        service.filter_result = {
            "is_safe": False,
            "filtered_content": "",
            "reason": "inappropriate",
        }
        service.topic_validation_result = False

        # Test unsafe content
        result = await service.filter_content("inappropriate content", 6)
        assert result["is_safe"] is False
        assert result["reason"] == "inappropriate"

        # Test invalid topic
        result = await service.validate_topic("violence", "child_456")
        assert result is False

    @pytest.mark.asyncio
    async def test_email_service_failure(self):
        """Test email service failure."""
        service = MockEmailService()
        service.email_success = False

        # Test failed email sending
        result = await service.send_email("invalid@", "Test", "template", {})
        assert result is False

        # Test failed deletion warning
        result = await service.send_deletion_warning(
            "invalid@", "Alice", "2024-01-01", "url"
        )
        assert result is False

    def test_settings_provider_production_mode(self):
        """Test settings provider in production mode."""
        provider = MockSettingsProvider()
        provider.production_mode = True

        # Test production mode
        is_prod = provider.is_production()
        assert is_prod is True

    @pytest.mark.asyncio
    async def test_audit_logger_multiple_events(self):
        """Test audit logger with multiple events."""
        logger = MockAuditLogger()

        # Log multiple access events
        await logger.log_child_access(
            "parent_1", "child_1", "view", "192.168.1.1", True
        )
        await logger.log_child_access(
            "parent_2", "child_2", "edit", "192.168.1.2", False
        )

        assert len(logger.logged_access_events) == 2
        assert logger.logged_access_events[0]["success"] is True
        assert logger.logged_access_events[1]["success"] is False

        # Log multiple consent events
        await logger.log_consent_change(
            "parent_1", "child_1", "data_collection", "granted", {}
        )
        await logger.log_consent_change(
            "parent_1", "child_1", "data_sharing", "revoked", {}
        )

        assert len(logger.logged_consent_events) == 2
        assert logger.logged_consent_events[0]["action"] == "granted"
        assert logger.logged_consent_events[1]["action"] == "revoked"

    @pytest.mark.asyncio
    async def test_event_bus_multiple_subscriptions(self):
        """Test event bus with multiple subscriptions."""
        bus = MockEventBus()

        # Subscribe multiple handlers to same event
        def handler1(event):
            return "handler1"

        def handler2(event):
            return "handler2"

        await bus.subscribe_to_events(["test_event"], handler1)
        await bus.subscribe_to_events(["test_event"], handler2)

        assert len(bus.subscriptions["test_event"]) == 2
        assert handler1 in bus.subscriptions["test_event"]
        assert handler2 in bus.subscriptions["test_event"]

    @pytest.mark.asyncio
    async def test_interface_method_signatures(self):
        """Test that interface methods have correct signatures."""
        # This test ensures that all interface methods are properly defined
        # and have the expected signatures

        # Test IEncryptionService
        service = MockEncryptionService()
        assert hasattr(service, "encrypt_child_data")
        assert hasattr(service, "decrypt_child_data")
        assert hasattr(service, "rotate_keys")

        # Test IDataRetentionService
        retention_service = MockDataRetentionService()
        assert hasattr(retention_service, "schedule_deletion")
        assert hasattr(retention_service, "export_child_data")
        assert hasattr(retention_service, "delete_expired_data")

        # Test all other services have required methods
        verification_service = MockParentVerificationService()
        assert hasattr(verification_service, "verify_parent_identity")
        assert hasattr(verification_service, "get_verification_methods")

        audit_logger = MockAuditLogger()
        assert hasattr(audit_logger, "log_child_access")
        assert hasattr(audit_logger, "log_consent_change")

        access_control = MockAccessControlService()
        assert hasattr(access_control, "verify_parent_child_access")
        assert hasattr(access_control, "get_parent_children")

        content_filter = MockContentFilterService()
        assert hasattr(content_filter, "filter_content")
        assert hasattr(content_filter, "validate_topic")

        email_service = MockEmailService()
        assert hasattr(email_service, "send_email")
        assert hasattr(email_service, "send_deletion_warning")

        settings_provider = MockSettingsProvider()
        assert hasattr(settings_provider, "get_database_url")
        assert hasattr(settings_provider, "get_encryption_key")
        assert hasattr(settings_provider, "get_coppa_settings")
        assert hasattr(settings_provider, "is_production")

        event_bus = MockEventBus()
        assert hasattr(event_bus, "publish_event")
        assert hasattr(event_bus, "subscribe_to_events")

    @pytest.mark.asyncio
    async def test_interface_return_types(self):
        """Test that interface methods return correct types."""
        # Test encryption service return types
        encryption_service = MockEncryptionService()

        encrypted = await encryption_service.encrypt_child_data("test")
        assert isinstance(encrypted, str)

        decrypted = await encryption_service.decrypt_child_data(encrypted)
        assert isinstance(decrypted, str)

        rotate_result = await encryption_service.rotate_keys()
        assert isinstance(rotate_result, bool)

        # Test data retention service return types
        retention_service = MockDataRetentionService()

        export_result = await retention_service.export_child_data("child_123")
        assert isinstance(export_result, str)

        delete_result = await retention_service.delete_expired_data()
        assert isinstance(delete_result, list)

        # Test parent verification service return types
        verification_service = MockParentVerificationService()

        verify_result = await verification_service.verify_parent_identity(
            "parent_123", "email", {}
        )
        assert isinstance(verify_result, bool)

        methods = await verification_service.get_verification_methods()
        assert isinstance(methods, list)

        # Test access control service return types
        access_control = MockAccessControlService()

        access_result = await access_control.verify_parent_child_access(
            "parent_123", "child_456", "read"
        )
        assert isinstance(access_result, bool)

        children = await access_control.get_parent_children("parent_123")
        assert isinstance(children, list)

        # Test content filter service return types
        content_filter = MockContentFilterService()

        filter_result = await content_filter.filter_content("test", 8)
        assert isinstance(filter_result, dict)

        topic_result = await content_filter.validate_topic("animals", "child_123")
        assert isinstance(topic_result, bool)

        # Test email service return types
        email_service = MockEmailService()

        send_result = await email_service.send_email(
            "test@example.com", "Subject", "template", {}
        )
        assert isinstance(send_result, bool)

        warning_result = await email_service.send_deletion_warning(
            "test@example.com", "Alice", "2024-01-01", "url"
        )
        assert isinstance(warning_result, bool)

        # Test settings provider return types
        settings_provider = MockSettingsProvider()

        db_url = settings_provider.get_database_url()
        assert isinstance(db_url, str)

        encryption_key = settings_provider.get_encryption_key()
        assert isinstance(encryption_key, str)

        coppa_settings = settings_provider.get_coppa_settings()
        assert isinstance(coppa_settings, dict)

        is_prod = settings_provider.is_production()
        assert isinstance(is_prod, bool)
