"""Tests for Comprehensive Audit Integration
Testing centralized audit logging service for all critical operations.
"""

from datetime import datetime
from unittest.mock import AsyncMock, Mock, patch

import pytest

from src.infrastructure.security.comprehensive_audit_integration import (
    AuditableOperation,
    ComprehensiveAuditIntegration,
    audit_authentication,
    audit_authorization,
    audit_child_data_operation,
    audit_coppa_event,
    audit_security_event,
    get_audit_integration,
)


class TestAuditableOperation:
    """Test the AuditableOperation dataclass."""

    def test_auditable_operation_creation_required_fields(self):
        """Test AuditableOperation creation with required fields only."""
        operation = AuditableOperation(
            operation_type="login",
            user_id="user_123",
            child_id=None,
            resource_id=None,
            ip_address="192.168.1.100",
        )

        assert operation.operation_type == "login"
        assert operation.user_id == "user_123"
        assert operation.child_id is None
        assert operation.resource_id is None
        assert operation.ip_address == "192.168.1.100"
        assert operation.details is None

    def test_auditable_operation_creation_all_fields(self):
        """Test AuditableOperation creation with all fields."""
        details = {"method": "email", "duration": 150}

        operation = AuditableOperation(
            operation_type="data_access",
            user_id="parent_456",
            child_id="child_789",
            resource_id="profile_123",
            ip_address="10.0.0.1",
            details=details,
        )

        assert operation.operation_type == "data_access"
        assert operation.user_id == "parent_456"
        assert operation.child_id == "child_789"
        assert operation.resource_id == "profile_123"
        assert operation.ip_address == "10.0.0.1"
        assert operation.details == details


class TestComprehensiveAuditIntegration:
    """Test the Comprehensive Audit Integration service."""

    @pytest.fixture
    def mock_audit_logger(self):
        """Create a mock audit logger."""
        mock_logger = Mock()
        mock_logger.log_event = AsyncMock(return_value="audit_event_123")

        with patch(
            "src.infrastructure.security.comprehensive_audit_integration.get_audit_logger",
            return_value=mock_logger,
        ):
            yield mock_logger

    @pytest.fixture
    def audit_integration(self, mock_audit_logger):
        """Create an audit integration instance."""
        return ComprehensiveAuditIntegration()

    @pytest.fixture
    def mock_datetime(self):
        """Mock datetime for consistent testing."""
        with patch(
            "src.infrastructure.security.comprehensive_audit_integration.datetime"
        ) as mock_dt:
            mock_dt.utcnow.return_value = datetime(2024, 1, 15, 10, 30, 0)
            yield mock_dt

    def test_initialization(self, audit_integration, mock_audit_logger):
        """Test audit integration initialization."""
        assert isinstance(audit_integration, ComprehensiveAuditIntegration)
        assert audit_integration.audit_logger == mock_audit_logger

    @pytest.mark.asyncio
    async def test_log_authentication_event_success(
        self, audit_integration, mock_audit_logger, mock_datetime
    ):
        """Test logging successful authentication event."""
        result = await audit_integration.log_authentication_event(
            event_type="login",
            user_email="user@example.com",
            success=True,
            ip_address="192.168.1.100",
            details={"method": "password"},
        )

        assert result == "audit_event_123"

        # Verify audit logger was called correctly
        mock_audit_logger.log_event.assert_called_once()
        call_kwargs = mock_audit_logger.log_event.call_args[1]

        assert call_kwargs["category"].value == "authentication"
        assert call_kwargs["severity"].value == "info"
        assert "Authentication login" in call_kwargs["description"]
        # Sanitized email
        assert call_kwargs["context"].user_id == "us***@example.com"
        assert call_kwargs["context"].ip_address == "192.168.1.100"
        assert call_kwargs["details"]["success"] is True
        assert call_kwargs["details"]["method"] == "password"

    @pytest.mark.asyncio
    async def test_log_authentication_event_failure(
        self, audit_integration, mock_audit_logger, mock_datetime
    ):
        """Test logging failed authentication event."""
        result = await audit_integration.log_authentication_event(
            event_type="login",
            user_email="failed@example.com",
            success=False,
            ip_address="192.168.1.101",
            details={"reason": "invalid_password"},
        )

        # Verify failure case handling
        call_kwargs = mock_audit_logger.log_event.call_args[1]
        assert call_kwargs["severity"].value == "warning"
        assert call_kwargs["details"]["success"] is False
        assert call_kwargs["details"]["reason"] == "invalid_password"

    @pytest.mark.asyncio
    async def test_log_authentication_event_account_locked(
        self, audit_integration, mock_audit_logger, mock_datetime
    ):
        """Test logging account locked event."""
        await audit_integration.log_authentication_event(
            event_type="account_locked",
            user_email="locked@example.com",
            success=False,
            ip_address="192.168.1.102",
        )

        # Account locked should have error severity
        call_kwargs = mock_audit_logger.log_event.call_args[1]
        assert call_kwargs["severity"].value == "error"

    @pytest.mark.asyncio
    async def test_log_authentication_event_different_types(
        self, audit_integration, mock_audit_logger, mock_datetime
    ):
        """Test logging different authentication event types."""
        auth_types = ["login", "logout", "password_change", "unknown_type"]

        for auth_type in auth_types:
            mock_audit_logger.reset_mock()

            await audit_integration.log_authentication_event(
                event_type=auth_type,
                user_email="test@example.com",
                success=True,
            )

            # Should handle all types gracefully
            mock_audit_logger.log_event.assert_called_once()

    @pytest.mark.asyncio
    async def test_log_authorization_event_granted(
        self, audit_integration, mock_audit_logger, mock_datetime
    ):
        """Test logging authorization granted event."""
        result = await audit_integration.log_authorization_event(
            user_id="parent_123",
            resource="child_profile",
            action="read",
            granted=True,
            child_id="child_456",
            ip_address="192.168.1.200",
            details={"permission_level": "full"},
        )

        assert result == "audit_event_123"

        # Verify audit logging
        call_kwargs = mock_audit_logger.log_event.call_args[1]
        assert call_kwargs["category"].value == "authorization"
        assert call_kwargs["severity"].value == "info"
        assert "Access read on child_profile: granted" in call_kwargs["description"]
        assert call_kwargs["context"].user_id == "parent_123"
        assert call_kwargs["context"].child_id == "child_456"
        assert call_kwargs["details"]["granted"] is True
        assert call_kwargs["details"]["permission_level"] == "full"

    @pytest.mark.asyncio
    async def test_log_authorization_event_denied(
        self, audit_integration, mock_audit_logger, mock_datetime
    ):
        """Test logging authorization denied event."""
        await audit_integration.log_authorization_event(
            user_id="unauthorized_user",
            resource="admin_panel",
            action="access",
            granted=False,
            ip_address="192.168.1.201",
            details={"reason": "insufficient_privileges"},
        )

        # Verify denial case handling
        call_kwargs = mock_audit_logger.log_event.call_args[1]
        assert call_kwargs["severity"].value == "warning"
        assert call_kwargs["details"]["granted"] is False
        assert call_kwargs["details"]["reason"] == "insufficient_privileges"

    @pytest.mark.asyncio
    async def test_log_child_data_operation_create(
        self, audit_integration, mock_audit_logger, mock_datetime
    ):
        """Test logging child data creation operation."""
        result = await audit_integration.log_child_data_operation(
            operation="create",
            child_id="child_new_123",
            user_id="parent_789",
            data_type="profile",
            ip_address="192.168.1.250",
            details={"fields_created": ["name", "age"]},
        )

        assert result == "audit_event_123"

        # Verify child data operation logging
        call_kwargs = mock_audit_logger.log_event.call_args[1]
        assert call_kwargs["category"].value == "data_protection"
        assert call_kwargs["severity"].value == "info"
        assert "Child data create: profile" in call_kwargs["description"]
        assert call_kwargs["context"].user_id == "parent_789"
        # Sanitized child ID
        assert call_kwargs["context"].child_id == "chil***123"
        assert call_kwargs["details"]["operation"] == "create"
        assert call_kwargs["details"]["data_type"] == "profile"

    @pytest.mark.asyncio
    async def test_log_child_data_operation_delete_sensitive(
        self, audit_integration, mock_audit_logger, mock_datetime
    ):
        """Test logging child data deletion with sensitive data type."""
        await audit_integration.log_child_data_operation(
            operation="delete",
            child_id="child_sensitive_456",
            user_id="parent_admin",
            data_type="medical",  # Sensitive data type
            details={"reason": "data_retention_expired"},
        )

        # Delete operation and sensitive data should have warning severity
        call_kwargs = mock_audit_logger.log_event.call_args[1]
        assert call_kwargs["severity"].value == "warning"

    @pytest.mark.asyncio
    async def test_log_child_data_operation_different_operations(
        self, audit_integration, mock_audit_logger, mock_datetime
    ):
        """Test logging different child data operations."""
        operations = [
            "create",
            "read",
            "update",
            "delete",
            "unknown_operation",
        ]

        for operation in operations:
            mock_audit_logger.reset_mock()

            await audit_integration.log_child_data_operation(
                operation=operation,
                child_id="child_test",
                user_id="user_test",
                data_type="test_data",
            )

            # Should handle all operations gracefully
            mock_audit_logger.log_event.assert_called_once()

    @pytest.mark.asyncio
    async def test_log_coppa_compliance_event(
        self, audit_integration, mock_audit_logger, mock_datetime
    ):
        """Test logging COPPA compliance event."""
        with patch(
            "src.infrastructure.security.comprehensive_audit_integration.requires_coppa_audit_logging",
            return_value=True,
        ):
            result = await audit_integration.log_coppa_compliance_event(
                event_type="consent_granted",
                child_id="coppa_child_789",
                parent_id="verified_parent_123",
                description="Parental consent granted for data collection",
                details={"verification_method": "government_id"},
            )

        assert result == "audit_event_123"

        # Verify COPPA compliance logging
        call_kwargs = mock_audit_logger.log_event.call_args[1]
        assert call_kwargs["category"].value == "coppa_compliance"
        assert call_kwargs["severity"].value == "info"
        assert call_kwargs["context"].user_id == "verified_parent_123"
        # Sanitized child ID
        assert call_kwargs["context"].child_id == "copp***789"
        assert call_kwargs["details"]["verification_method"] == "government_id"

    @pytest.mark.asyncio
    async def test_log_coppa_compliance_event_disabled(
        self, audit_integration, mock_audit_logger, mock_datetime
    ):
        """Test logging COPPA compliance event when COPPA is disabled."""
        with patch(
            "src.infrastructure.security.comprehensive_audit_integration.requires_coppa_audit_logging",
            return_value=False,
        ):
            result = await audit_integration.log_coppa_compliance_event(
                event_type="consent_granted",
                child_id="coppa_child_disabled",
                parent_id="parent_disabled",
                description="Test description",
            )

        # Should return mock ID when COPPA is disabled
        assert result.startswith("coppa_disabled_consent_granted_")

        # Should not call audit logger when COPPA is disabled
        mock_audit_logger.log_event.assert_not_called()

    @pytest.mark.asyncio
    async def test_log_coppa_compliance_different_event_types(
        self, audit_integration, mock_audit_logger, mock_datetime
    ):
        """Test logging different COPPA compliance event types."""
        coppa_events = [
            "consent_requested",
            "consent_granted",
            "consent_revoked",
            "data_retention_triggered",
            "data_deleted",
            "unknown_coppa_event",
        ]

        with patch(
            "src.infrastructure.security.comprehensive_audit_integration.requires_coppa_audit_logging",
            return_value=True,
        ):
            for event_type in coppa_events:
                mock_audit_logger.reset_mock()

                await audit_integration.log_coppa_compliance_event(
                    event_type=event_type,
                    child_id="test_child",
                    parent_id="test_parent",
                    description=f"Test {event_type}",
                )

                # Should handle all event types gracefully
                mock_audit_logger.log_event.assert_called_once()

    @pytest.mark.asyncio
    async def test_log_security_event(
        self, audit_integration, mock_audit_logger, mock_datetime
    ):
        """Test logging security event."""
        result = await audit_integration.log_security_event(
            event_type="rate_limit_exceeded",
            severity="warning",
            description="Rate limit exceeded for user",
            user_id="suspicious_user_123",
            ip_address="192.168.1.999",
            details={"attempts": 100, "window": "60s"},
        )

        assert result == "audit_event_123"

        # Verify security event logging
        call_kwargs = mock_audit_logger.log_event.call_args[1]
        assert call_kwargs["category"].value == "system_security"
        assert call_kwargs["severity"].value == "warning"
        assert call_kwargs["context"].user_id == "suspicious_user_123"
        assert call_kwargs["context"].ip_address == "192.168.1.999"
        assert call_kwargs["details"]["attempts"] == 100
        assert call_kwargs["details"]["window"] == "60s"

    @pytest.mark.asyncio
    async def test_log_security_event_different_severities(
        self, audit_integration, mock_audit_logger, mock_datetime
    ):
        """Test logging security events with different severity levels."""
        severities = [
            "debug",
            "info",
            "warning",
            "error",
            "critical",
            "unknown_severity",
        ]

        for severity in severities:
            mock_audit_logger.reset_mock()

            await audit_integration.log_security_event(
                event_type="test_event",
                severity=severity,
                description=f"Test event with {severity} severity",
            )

            # Should handle all severities gracefully
            mock_audit_logger.log_event.assert_called_once()

    @pytest.mark.asyncio
    async def test_log_system_event(
        self, audit_integration, mock_audit_logger, mock_datetime
    ):
        """Test logging system event."""
        result = await audit_integration.log_system_event(
            event_type="startup",
            description="System startup completed",
            details={"version": "1.0.0", "startup_time": "2.5s"},
        )

        assert result == "audit_event_123"

        # Verify system event logging
        call_kwargs = mock_audit_logger.log_event.call_args[1]
        assert call_kwargs["category"].value == "system_security"
        assert call_kwargs["severity"].value == "info"
        assert call_kwargs["description"] == "System startup completed"
        assert call_kwargs["details"]["version"] == "1.0.0"
        assert call_kwargs["details"]["startup_time"] == "2.5s"

    @pytest.mark.asyncio
    async def test_log_system_event_different_types(
        self, audit_integration, mock_audit_logger, mock_datetime
    ):
        """Test logging different system event types."""
        system_events = [
            "startup",
            "shutdown",
            "config_change",
            "unknown_system_event",
        ]

        for event_type in system_events:
            mock_audit_logger.reset_mock()

            await audit_integration.log_system_event(
                event_type=event_type, description=f"Test {event_type} event"
            )

            # Should handle all event types gracefully
            mock_audit_logger.log_event.assert_called_once()

    def test_sanitize_email(self, audit_integration):
        """Test email sanitization for COPPA compliance."""
        test_cases = [
            ("user@example.com", "us***@example.com"),
            ("a@b.co", "a***@b.co"),
            ("verylongemail@domain.org", "ve***@domain.org"),
            ("invalid-email", "***@***"),
            ("", "***@***"),
            (None, "***@***"),
        ]

        for email, expected in test_cases:
            result = audit_integration._sanitize_email(email)
            assert result == expected

    def test_sanitize_child_id(self, audit_integration):
        """Test child ID sanitization for COPPA compliance."""
        test_cases = [
            ("child_123456789", "chil***6789"),  # Long ID
            ("child123", "ch***"),  # Short ID
            ("abcdefghijk", "abcd***hijk"),  # Medium ID
            ("ab", "ab***"),  # Very short ID
            ("", "***"),  # Empty ID
            (None, "***"),  # None ID
        ]

        for child_id, expected in test_cases:
            result = audit_integration._sanitize_child_id(child_id)
            assert result == expected

    def test_get_audit_integration_singleton(self):
        """Test global audit integration singleton."""
        # Clear the global instance
        import src.infrastructure.security.comprehensive_audit_integration as audit_module

        audit_module._audit_integration = None

        # Get first instance
        integration1 = get_audit_integration()
        assert integration1 is not None

        # Get second instance - should be the same
        integration2 = get_audit_integration()
        assert integration1 is integration2

    @pytest.mark.asyncio
    async def test_audit_authentication_convenience_function(self, mock_audit_logger):
        """Test audit_authentication convenience function."""
        # Clear global instance to ensure clean test
        import src.infrastructure.security.comprehensive_audit_integration as audit_module

        audit_module._audit_integration = None

        result = await audit_authentication(
            event_type="login",
            user_email="convenience@example.com",
            success=True,
            ip_address="192.168.1.300",
        )

        assert result == "audit_event_123"

    @pytest.mark.asyncio
    async def test_audit_authorization_convenience_function(self, mock_audit_logger):
        """Test audit_authorization convenience function."""
        import src.infrastructure.security.comprehensive_audit_integration as audit_module

        audit_module._audit_integration = None

        result = await audit_authorization(
            user_id="convenience_user",
            resource="convenience_resource",
            action="convenience_action",
            granted=True,
        )

        assert result == "audit_event_123"

    @pytest.mark.asyncio
    async def test_audit_child_data_operation_convenience_function(
        self, mock_audit_logger
    ):
        """Test audit_child_data_operation convenience function."""
        import src.infrastructure.security.comprehensive_audit_integration as audit_module

        audit_module._audit_integration = None

        result = await audit_child_data_operation(
            operation="read",
            child_id="convenience_child",
            user_id="convenience_parent",
            data_type="convenience_data",
        )

        assert result == "audit_event_123"

    @pytest.mark.asyncio
    async def test_audit_coppa_event_convenience_function(self, mock_audit_logger):
        """Test audit_coppa_event convenience function."""
        import src.infrastructure.security.comprehensive_audit_integration as audit_module

        audit_module._audit_integration = None

        with patch(
            "src.infrastructure.security.comprehensive_audit_integration.requires_coppa_audit_logging",
            return_value=True,
        ):
            result = await audit_coppa_event(
                event_type="consent_granted",
                child_id="convenience_coppa_child",
                parent_id="convenience_coppa_parent",
                description="Convenience COPPA test",
            )

        assert result == "audit_event_123"

    @pytest.mark.asyncio
    async def test_audit_security_event_convenience_function(self, mock_audit_logger):
        """Test audit_security_event convenience function."""
        import src.infrastructure.security.comprehensive_audit_integration as audit_module

        audit_module._audit_integration = None

        result = await audit_security_event(
            event_type="convenience_security",
            severity="info",
            description="Convenience security test",
        )

        assert result == "audit_event_123"

    @pytest.mark.asyncio
    async def test_concurrent_audit_operations(
        self, audit_integration, mock_audit_logger, mock_datetime
    ):
        """Test concurrent audit operations."""
        import asyncio

        # Create multiple concurrent audit operations
        tasks = [
            audit_integration.log_authentication_event(
                "login", "user1@example.com", True
            ),
            audit_integration.log_authorization_event(
                "user2", "resource", "action", True
            ),
            audit_integration.log_child_data_operation(
                "read", "child1", "parent1", "profile"
            ),
            audit_integration.log_security_event(
                "test_event", "info", "Test description"
            ),
            audit_integration.log_system_event("test_system", "System test"),
        ]

        results = await asyncio.gather(*tasks)

        # All should succeed
        assert len(results) == 5
        assert all(result == "audit_event_123" for result in results)

        # Audit logger should have been called for each operation
        assert mock_audit_logger.log_event.call_count == 5

    @pytest.mark.asyncio
    async def test_comprehensive_audit_workflow(
        self, audit_integration, mock_audit_logger, mock_datetime
    ):
        """Test comprehensive audit workflow covering all event types."""
        # Simulate a complete user workflow
        workflow_events = [
            # 1. User logs in
            (
                "auth",
                audit_integration.log_authentication_event(
                    "login", "workflow@example.com", True
                ),
            ),
            # 2. User accesses child profile
            (
                "authz",
                audit_integration.log_authorization_event(
                    "workflow_user",
                    "child_profile",
                    "read",
                    True,
                    "workflow_child",
                ),
            ),
            # 3. User reads child data
            (
                "data",
                audit_integration.log_child_data_operation(
                    "read", "workflow_child", "workflow_user", "profile"
                ),
            ),
            # 4. COPPA event for data access
            (
                "coppa",
                audit_integration.log_coppa_compliance_event(
                    "data_accessed",
                    "workflow_child",
                    "workflow_user",
                    "Child data accessed",
                ),
            ),
            # 5. Security event for activity monitoring
            (
                "security",
                audit_integration.log_security_event(
                    "user_activity", "info", "User activity monitored"
                ),
            ),
            # 6. User logs out
            (
                "logout",
                audit_integration.log_authentication_event(
                    "logout", "workflow@example.com", True
                ),
            ),
        ]

        # Execute workflow with COPPA enabled
        with patch(
            "src.infrastructure.security.comprehensive_audit_integration.requires_coppa_audit_logging",
            return_value=True,
        ):
            results = []
            for event_type, coro in workflow_events:
                result = await coro
                results.append((event_type, result))

        # All events should be logged successfully
        assert len(results) == 6
        assert all(result[1] == "audit_event_123" for result in results)

        # Verify all audit events were logged
        assert mock_audit_logger.log_event.call_count == 6

    @pytest.mark.asyncio
    async def test_error_handling_in_audit_operations(
        self, audit_integration, mock_datetime
    ):
        """Test error handling in audit operations."""
        # Mock audit logger to raise exception
        mock_failing_logger = Mock()
        mock_failing_logger.log_event = AsyncMock(
            side_effect=Exception("Audit logging error")
        )

        with patch(
            "src.infrastructure.security.comprehensive_audit_integration.get_audit_logger",
            return_value=mock_failing_logger,
        ):
            audit_integration_failing = ComprehensiveAuditIntegration()

            # Should propagate the exception (caller should handle)
            with pytest.raises(Exception, match="Audit logging error"):
                await audit_integration_failing.log_authentication_event(
                    "login", "error@example.com", True
                )

    @pytest.mark.asyncio
    async def test_edge_cases_invalid_inputs(
        self, audit_integration, mock_audit_logger, mock_datetime
    ):
        """Test handling of edge cases with invalid inputs."""
        # Test with various invalid/edge case inputs
        edge_cases = [
            # Empty strings
            ("", "", True),
            # None values where strings expected
            (None, None, True),
            # Very long strings
            (
                "very_long_event_type_" + "x" * 100,
                "very_long_email_" + "x" * 100 + "@example.com",
                True,
            ),
            # Special characters
            ("login@#$%", "user+special@example.com", True),
        ]

        for event_type, email, success in edge_cases:
            try:
                result = await audit_integration.log_authentication_event(
                    event_type, email, success
                )
                # Should handle gracefully and return audit event ID
                assert result == "audit_event_123"
            except Exception as e:
                # Some edge cases might raise exceptions, which is acceptable
                assert isinstance(e, (TypeError, AttributeError))

    @pytest.mark.asyncio
    async def test_audit_context_propagation(
        self, audit_integration, mock_audit_logger, mock_datetime
    ):
        """Test that audit context is properly propagated through all audit methods."""
        # Test that context information is preserved and passed correctly
        test_user_id = "context_test_user"
        test_child_id = "context_test_child"
        test_ip = "192.168.1.999"

        await audit_integration.log_authorization_event(
            user_id=test_user_id,
            resource="test_resource",
            action="test_action",
            granted=True,
            child_id=test_child_id,
            ip_address=test_ip,
        )

        # Verify context was properly set
        call_kwargs = mock_audit_logger.log_event.call_args[1]
        context = call_kwargs["context"]

        assert context.user_id == test_user_id
        assert context.child_id == test_child_id
        assert context.ip_address == test_ip

    def test_sanitization_performance(self, audit_integration):
        """Test performance of sanitization methods with large inputs."""
        import time

        # Test with large email
        large_email = "a" * 1000 + "@" + "b" * 1000 + ".com"

        start_time = time.time()
        for _ in range(1000):
            audit_integration._sanitize_email(large_email)
        end_time = time.time()

        # Should complete quickly (less than 1 second for 1000 operations)
        assert (end_time - start_time) < 1.0

        # Test with large child ID
        large_child_id = "child_" + "x" * 1000

        start_time = time.time()
        for _ in range(1000):
            audit_integration._sanitize_child_id(large_child_id)
        end_time = time.time()

        # Should complete quickly
        assert (end_time - start_time) < 1.0
