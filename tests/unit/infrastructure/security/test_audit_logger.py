"""Tests for Audit Logger
Testing comprehensive audit logging system for COPPA compliance and security.
"""

import asyncio
import os
import shutil
import tempfile
from datetime import datetime
from unittest.mock import mock_open, patch

import pytest

from src.infrastructure.security.audit.audit_logger import (
    AuditCategory,
    AuditConfig,
    AuditContext,
    AuditEvent,
    AuditEventType,
    AuditLogger,
    AuditSeverity,
    get_audit_logger,
    log_audit_event,
    log_child_safety_incident,
)


class TestAuditLogger:
    """Test the Audit Logger."""

    @pytest.fixture
    def temp_dir(self):
        """Create temporary directory for audit logs."""
        temp_dir = tempfile.mkdtemp()
        yield temp_dir
        shutil.rmtree(temp_dir)

    @pytest.fixture
    def audit_config(self, temp_dir):
        """Create audit configuration for testing."""
        return AuditConfig(
            log_directory=temp_dir,
            max_file_size_mb=10,
            max_files=5,
            retention_days=30,
            enable_encryption=True,
            enable_tamper_detection=True,
            batch_size=10,
            flush_interval_seconds=1.0,
        )

    @pytest.fixture
    def audit_logger(self, audit_config):
        """Create audit logger instance."""
        with patch.object(AuditLogger, "_start_background_tasks"):
            return AuditLogger(audit_config)

    def test_audit_category_enum_values(self):
        """Test AuditCategory enum values."""
        assert AuditCategory.AUTHENTICATION.value == "authentication"
        assert AuditCategory.AUTHORIZATION.value == "authorization"
        assert AuditCategory.CHILD_SAFETY.value == "child_safety"
        assert AuditCategory.DATA_PROTECTION.value == "data_protection"
        assert AuditCategory.SYSTEM_SECURITY.value == "system_security"
        assert AuditCategory.COPPA_COMPLIANCE.value == "coppa_compliance"
        assert AuditCategory.PARENT_VERIFICATION.value == "parent_verification"
        assert AuditCategory.DATA_RETENTION.value == "data_retention"
        assert AuditCategory.ENCRYPTION.value == "encryption"
        assert AuditCategory.ACCESS_CONTROL.value == "access_control"

    def test_audit_event_type_enum_values(self):
        """Test AuditEventType enum values."""
        # Authentication events
        assert AuditEventType.LOGIN_SUCCESS.value == "login_success"
        assert AuditEventType.LOGIN_FAILURE.value == "login_failure"
        assert AuditEventType.LOGOUT.value == "logout"

        # Child safety events
        assert AuditEventType.CHILD_INTERACTION_START.value == "child_interaction_start"
        assert AuditEventType.SAFETY_INCIDENT.value == "safety_incident"
        assert AuditEventType.CONTENT_FILTERED.value == "content_filtered"

        # Data protection events
        assert AuditEventType.DATA_ACCESS.value == "data_access"
        assert AuditEventType.DATA_MODIFICATION.value == "data_modification"
        assert AuditEventType.DATA_DELETION.value == "data_deletion"

        # COPPA compliance events
        assert (
            AuditEventType.PARENTAL_CONSENT_REQUEST.value == "parental_consent_request"
        )
        assert (
            AuditEventType.PARENTAL_CONSENT_GRANTED.value == "parental_consent_granted"
        )
        assert (
            AuditEventType.PARENTAL_CONSENT_REVOKED.value == "parental_consent_revoked"
        )

    def test_audit_severity_enum_values(self):
        """Test AuditSeverity enum values."""
        assert AuditSeverity.DEBUG.value == "debug"
        assert AuditSeverity.INFO.value == "info"
        assert AuditSeverity.WARNING.value == "warning"
        assert AuditSeverity.ERROR.value == "error"
        assert AuditSeverity.CRITICAL.value == "critical"

    def test_audit_config_initialization(self, audit_config):
        """Test AuditConfig initialization."""
        assert audit_config.max_file_size_mb == 10
        assert audit_config.max_files == 5
        assert audit_config.retention_days == 30
        assert audit_config.enable_encryption is True
        assert audit_config.enable_tamper_detection is True
        assert audit_config.batch_size == 10
        assert audit_config.flush_interval_seconds == 1.0

    def test_audit_context_initialization(self):
        """Test AuditContext initialization."""
        context = AuditContext(
            user_id="user_123",
            child_id="child_456",
            session_id="session_789",
            ip_address="192.168.1.100",
        )

        assert context.user_id == "user_123"
        assert context.child_id == "child_456"
        assert context.session_id == "session_789"
        assert context.ip_address == "192.168.1.100"

    def test_audit_event_initialization(self):
        """Test AuditEvent initialization."""
        context = AuditContext(user_id="user_123")
        details = {"key": "value"}

        event = AuditEvent(
            event_id="event_123",
            timestamp=datetime.utcnow(),
            event_type=AuditEventType.LOGIN_SUCCESS,
            severity=AuditSeverity.INFO,
            category=AuditCategory.AUTHENTICATION,
            description="User login successful",
            context=context,
            details=details,
        )

        assert event.event_id == "event_123"
        assert event.event_type == AuditEventType.LOGIN_SUCCESS
        assert event.severity == AuditSeverity.INFO
        assert event.category == AuditCategory.AUTHENTICATION
        assert event.description == "User login successful"
        assert event.context == context
        assert event.details == details

    def test_audit_event_to_dict(self):
        """Test AuditEvent to_dict conversion."""
        timestamp = datetime.utcnow()
        context = AuditContext(user_id="user_123")
        details = {"operation": "read"}

        event = AuditEvent(
            event_id="event_dict",
            timestamp=timestamp,
            event_type=AuditEventType.DATA_ACCESS,
            severity=AuditSeverity.INFO,
            category=AuditCategory.DATA_PROTECTION,
            description="Data access event",
            context=context,
            details=details,
        )

        result_dict = event.to_dict()

        assert result_dict["event_id"] == "event_dict"
        assert result_dict["timestamp"] == timestamp.isoformat()
        assert result_dict["event_type"] == "data_access"
        assert result_dict["severity"] == "info"
        assert result_dict["category"] == "data_protection"
        assert result_dict["description"] == "Data access event"
        assert result_dict["context"]["user_id"] == "user_123"
        assert result_dict["details"] == details

    def test_audit_event_calculate_checksum(self):
        """Test AuditEvent checksum calculation."""
        timestamp = datetime.utcnow()
        event = AuditEvent(
            event_id="checksum_test",
            timestamp=timestamp,
            event_type=AuditEventType.SYSTEM_STARTUP,
            severity=AuditSeverity.INFO,
            category=AuditCategory.SYSTEM_SECURITY,
            description="System startup",
        )

        checksum = event.calculate_checksum()

        assert isinstance(checksum, str)
        assert len(checksum) == 64  # SHA256 hex digest length

        # Same event should produce same checksum
        checksum2 = event.calculate_checksum()
        assert checksum == checksum2

        # Different event should produce different checksum
        event.description = "Different description"
        checksum3 = event.calculate_checksum()
        assert checksum != checksum3

    def test_audit_logger_initialization(self, audit_logger, audit_config):
        """Test AuditLogger initialization."""
        assert audit_logger.config == audit_config
        assert hasattr(audit_logger, "audit_entries")
        assert hasattr(audit_logger, "buffer_lock")
        assert isinstance(audit_logger.audit_entries, list)
        assert len(audit_logger.audit_entries) == 0

    def test_ensure_log_directory(self, audit_config, temp_dir):
        """Test log directory creation."""
        # Remove the directory to test creation
        if os.path.exists(temp_dir):
            shutil.rmtree(temp_dir)

        assert not os.path.exists(temp_dir)

        with patch.object(AuditLogger, "_start_background_tasks"):
            logger = AuditLogger(audit_config)

        assert os.path.exists(temp_dir)

    @pytest.mark.asyncio
    async def test_log_event_basic(self, audit_logger):
        """Test basic event logging."""
        event_id = await audit_logger.log_event(
            event_type=AuditEventType.LOGIN_SUCCESS,
            severity=AuditSeverity.INFO,
            category=AuditCategory.AUTHENTICATION,
            description="User logged in successfully",
        )

        assert isinstance(event_id, str)
        assert len(audit_logger.audit_entries) == 1

        logged_event = audit_logger.audit_entries[0]
        assert logged_event.event_id == event_id
        assert logged_event.event_type == AuditEventType.LOGIN_SUCCESS
        assert logged_event.severity == AuditSeverity.INFO
        assert logged_event.category == AuditCategory.AUTHENTICATION
        assert logged_event.description == "User logged in successfully"

    @pytest.mark.asyncio
    async def test_log_event_with_context_and_details(self, audit_logger):
        """Test event logging with context and details."""
        context = AuditContext(user_id="user_456", ip_address="192.168.1.200")
        details = {"method": "email", "attempt_number": 1}

        event_id = await audit_logger.log_event(
            event_type=AuditEventType.LOGIN_FAILURE,
            severity=AuditSeverity.WARNING,
            category=AuditCategory.AUTHENTICATION,
            description="Login attempt failed",
            context=context,
            details=details,
        )

        logged_event = audit_logger.audit_entries[0]
        assert logged_event.context == context
        assert logged_event.details == details

    @pytest.mark.asyncio
    async def test_log_event_with_tamper_detection(self, audit_logger):
        """Test event logging with tamper detection enabled."""
        audit_logger.config.enable_tamper_detection = True

        await audit_logger.log_event(
            event_type=AuditEventType.DATA_ACCESS,
            severity=AuditSeverity.INFO,
            category=AuditCategory.DATA_PROTECTION,
            description="Data accessed",
        )

        logged_event = audit_logger.audit_entries[0]
        assert logged_event.checksum is not None
        assert len(logged_event.checksum) == 64

    @pytest.mark.asyncio
    async def test_log_event_critical_handling(self, audit_logger):
        """Test handling of critical events."""
        with patch.object(audit_logger, "_handle_critical_event") as mock_handle:
            await audit_logger.log_event(
                event_type=AuditEventType.SAFETY_INCIDENT,
                severity=AuditSeverity.CRITICAL,
                category=AuditCategory.CHILD_SAFETY,
                description="Critical safety incident",
            )

            mock_handle.assert_called_once()

    @pytest.mark.asyncio
    async def test_log_event_error_handling(self, audit_logger):
        """Test error handling in event logging."""
        # Mock an error in event creation
        with patch(
            "src.infrastructure.security.audit_logger.AuditEvent",
            side_effect=Exception("Event creation error"),
        ):
            event_id = await audit_logger.log_event(
                event_type=AuditEventType.SYSTEM_STARTUP,
                severity=AuditSeverity.INFO,
                category=AuditCategory.SYSTEM_SECURITY,
                description="System startup",
            )

            # Should still return an event ID even on error
            assert isinstance(event_id, str)

    @pytest.mark.asyncio
    async def test_log_child_interaction(self, audit_logger):
        """Test child interaction logging."""
        event_id = await audit_logger.log_child_interaction(
            child_id="child_789",
            interaction_type="chat",
            content="Hello, can you help me with my homework?",
            response="Of course! What subject do you need help with?",
            safety_score=0.95,
            parent_id="parent_123",
        )

        assert isinstance(event_id, str)
        assert len(audit_logger.audit_entries) == 1

        logged_event = audit_logger.audit_entries[0]
        assert logged_event.event_type == AuditEventType.CHILD_INTERACTION_START
        assert logged_event.category == AuditCategory.CHILD_SAFETY
        assert logged_event.context.child_id == "child_789"
        assert logged_event.context.user_id == "parent_123"
        assert logged_event.details["interaction_type"] == "chat"
        assert logged_event.details["safety_score"] == 0.95

    @pytest.mark.asyncio
    async def test_log_child_interaction_low_safety_score(self, audit_logger):
        """Test child interaction logging with low safety score."""
        event_id = await audit_logger.log_child_interaction(
            child_id="child_danger",
            interaction_type="voice",
            content="Inappropriate content",
            response="I cannot help with that",
            safety_score=0.2,
        )

        logged_event = audit_logger.audit_entries[0]
        assert logged_event.severity == AuditSeverity.CRITICAL
        assert logged_event.details["safety_score"] == 0.2

    @pytest.mark.asyncio
    async def test_log_child_interaction_medium_safety_score(self, audit_logger):
        """Test child interaction logging with medium safety score."""
        event_id = await audit_logger.log_child_interaction(
            child_id="child_medium",
            interaction_type="chat",
            content="Questionable content",
            response="Let me rephrase that",
            safety_score=0.5,
        )

        logged_event = audit_logger.audit_entries[0]
        assert logged_event.severity == AuditSeverity.WARNING

    @pytest.mark.asyncio
    async def test_log_child_interaction_content_hashing(self, audit_logger):
        """Test content hashing in child interaction logging."""
        audit_logger.config.enable_encryption = True

        long_content = "A" * 200
        long_response = "B" * 150

        await audit_logger.log_child_interaction(
            child_id="child_hash",
            interaction_type="chat",
            content=long_content,
            response=long_response,
            safety_score=0.8,
        )

        logged_event = audit_logger.audit_entries[0]
        details = logged_event.details

        # Should contain hashes, not full content
        # SHA256 truncated to 16 chars
        assert len(details["content_hash"]) == 16
        assert len(details["response_hash"]) == 16
        assert details["content_length"] == 200
        assert details["response_length"] == 150

    @pytest.mark.asyncio
    async def test_log_safety_incident(self, audit_logger):
        """Test safety incident logging."""
        incident_details = {
            "trigger": "inappropriate_content",
            "action_taken": "blocked_response",
        }

        event_id = await audit_logger.log_safety_incident(
            child_id="child_incident",
            incident_type="content_violation",
            description="Child attempted to share personal information",
            details=incident_details,
        )

        logged_event = audit_logger.audit_entries[0]
        assert logged_event.event_type == AuditEventType.SAFETY_INCIDENT
        assert logged_event.severity == AuditSeverity.CRITICAL
        assert logged_event.category == AuditCategory.CHILD_SAFETY
        assert logged_event.context.child_id == "child_incident"
        assert logged_event.details["incident_type"] == "content_violation"
        assert logged_event.details["auto_generated"] is True
        assert logged_event.details["requires_investigation"] is True
        assert logged_event.details["trigger"] == "inappropriate_content"

    @pytest.mark.asyncio
    async def test_log_data_access(self, audit_logger):
        """Test data access logging."""
        event_id = await audit_logger.log_data_access(
            user_id="parent_data",
            data_type="conversation_history",
            operation="read",
            resource_id="conv_12345",
            child_id="child_data",
            ip_address="192.168.1.50",
        )

        logged_event = audit_logger.audit_entries[0]
        assert logged_event.event_type == AuditEventType.DATA_ACCESS
        assert logged_event.category == AuditCategory.DATA_PROTECTION
        assert logged_event.context.user_id == "parent_data"
        assert logged_event.context.child_id == "child_data"
        assert logged_event.context.ip_address == "192.168.1.50"
        assert logged_event.details["data_type"] == "conversation_history"
        assert logged_event.details["operation"] == "read"
        assert logged_event.details["resource_id"] == "conv_12345"

    @pytest.mark.asyncio
    async def test_log_data_access_severity_escalation(self, audit_logger):
        """Test data access logging with severity escalation."""
        # Test delete operation - should be WARNING
        await audit_logger.log_data_access(
            user_id="user_delete",
            data_type="profile",
            operation="delete",
            resource_id="profile_123",
        )

        delete_event = audit_logger.audit_entries[0]
        assert delete_event.severity == AuditSeverity.WARNING

        # Test sensitive data access - should be WARNING
        await audit_logger.log_data_access(
            user_id="user_voice",
            data_type="voice",
            operation="read",
            resource_id="voice_456",
        )

        voice_event = audit_logger.audit_entries[1]
        assert voice_event.severity == AuditSeverity.WARNING

    @pytest.mark.asyncio
    async def test_log_coppa_event(self, audit_logger):
        """Test COPPA compliance event logging."""
        coppa_details = {
            "verification_method": "government_id",
            "consent_scope": "data_collection",
        }

        event_id = await audit_logger.log_coppa_event(
            event_type=AuditEventType.PARENTAL_CONSENT_GRANTED,
            child_id="coppa_child",
            parent_id="coppa_parent",
            description="Parental consent granted for data collection",
            details=coppa_details,
        )

        logged_event = audit_logger.audit_entries[0]
        assert logged_event.event_type == AuditEventType.PARENTAL_CONSENT_GRANTED
        assert logged_event.category == AuditCategory.COPPA_COMPLIANCE
        assert logged_event.severity == AuditSeverity.INFO
        assert logged_event.context.child_id == "coppa_child"
        assert logged_event.context.user_id == "coppa_parent"
        assert logged_event.details == coppa_details

    @pytest.mark.asyncio
    async def test_handle_critical_event(self, audit_logger):
        """Test critical event handling."""
        critical_event = AuditEvent(
            event_id="critical_123",
            timestamp=datetime.utcnow(),
            event_type=AuditEventType.SAFETY_INCIDENT,
            severity=AuditSeverity.CRITICAL,
            category=AuditCategory.CHILD_SAFETY,
            description="Critical safety incident",
        )

        with patch.object(audit_logger, "_write_events_to_file") as mock_write:
            with patch.object(audit_logger, "_send_security_alert") as mock_alert:
                await audit_logger._handle_critical_event(critical_event)

                mock_write.assert_called_once_with([critical_event])
                mock_alert.assert_called_once_with(critical_event)

    @pytest.mark.asyncio
    async def test_send_security_alert(self, audit_logger):
        """Test security alert sending."""
        critical_event = AuditEvent(
            event_id="alert_123",
            timestamp=datetime.utcnow(),
            event_type=AuditEventType.SAFETY_INCIDENT,
            severity=AuditSeverity.CRITICAL,
            category=AuditCategory.CHILD_SAFETY,
            description="Security alert test",
        )

        with patch("src.infrastructure.security.audit_logger.logger") as mock_logger:
            await audit_logger._send_security_alert(critical_event)

            mock_logger.critical.assert_called()
            call_args = mock_logger.critical.call_args[0][0]
            assert "SECURITY_ALERT" in call_args
            assert "alert_123" in call_args

    @pytest.mark.asyncio
    async def test_write_events_to_file(self, audit_logger):
        """Test writing events to file."""
        events = [
            AuditEvent(
                event_id="file_test_1",
                timestamp=datetime.utcnow(),
                event_type=AuditEventType.LOGIN_SUCCESS,
                severity=AuditSeverity.INFO,
                category=AuditCategory.AUTHENTICATION,
                description="Test event 1",
            ),
            AuditEvent(
                event_id="file_test_2",
                timestamp=datetime.utcnow(),
                event_type=AuditEventType.DATA_ACCESS,
                severity=AuditSeverity.INFO,
                category=AuditCategory.DATA_PROTECTION,
                description="Test event 2",
            ),
        ]

        # Mock aiofiles.open
        with patch(
            "src.infrastructure.security.audit_logger.aiofiles.open",
            mock_open(),
        ) as mock_file:
            await audit_logger._write_events_to_file(events)

            # Should have been called to open the file
            mock_file.assert_called_once()

            # Should have written 2 lines (one per event)
            handle = mock_file.return_value.__aenter__.return_value
            assert handle.write.call_count == 2

    @pytest.mark.asyncio
    async def test_write_events_empty_list(self, audit_logger):
        """Test writing empty events list."""
        with patch(
            "src.infrastructure.security.audit_logger.aiofiles.open"
        ) as mock_file:
            await audit_logger._write_events_to_file([])

            # Should not attempt to open file for empty list
            mock_file.assert_not_called()

    @pytest.mark.asyncio
    async def test_write_events_error_handling(self, audit_logger):
        """Test error handling in file writing."""
        events = [
            AuditEvent(
                event_id="error_test",
                timestamp=datetime.utcnow(),
                event_type=AuditEventType.SYSTEM_STARTUP,
                severity=AuditSeverity.INFO,
                category=AuditCategory.SYSTEM_SECURITY,
                description="Error test event",
            )
        ]

        with patch(
            "src.infrastructure.security.audit_logger.aiofiles.open",
            side_effect=Exception("File error"),
        ):
            # Should not raise exception
            await audit_logger._write_events_to_file(events)

    def test_get_audit_logger_singleton(self):
        """Test global audit logger singleton."""
        # Clear the global instance
        import src.infrastructure.security.audit_logger as audit_module

        audit_module._audit_logger = None

        # Get first instance
        logger1 = get_audit_logger()
        assert logger1 is not None

        # Get second instance - should be the same
        logger2 = get_audit_logger()
        assert logger1 is logger2

    def test_get_audit_logger_config(self):
        """Test global audit logger configuration."""
        # Clear the global instance
        import src.infrastructure.security.audit_logger as audit_module

        audit_module._audit_logger = None

        logger = get_audit_logger()
        config = logger.config

        assert config.log_directory == "logs/audit"
        assert config.max_file_size_mb == 100
        assert config.retention_days == 2555  # 7 years for COPPA
        assert config.enable_encryption is True
        assert config.enable_tamper_detection is True

    @pytest.mark.asyncio
    async def test_log_audit_event_convenience_function(self):
        """Test convenience function for logging audit events."""
        # Clear the global instance to ensure clean test
        import src.infrastructure.security.audit_logger as audit_module

        audit_module._audit_logger = None

        event_id = await log_audit_event(
            event_type=AuditEventType.LOGIN_SUCCESS,
            severity=AuditSeverity.INFO,
            category=AuditCategory.AUTHENTICATION,
            description="Convenience function test",
        )

        assert isinstance(event_id, str)

    @pytest.mark.asyncio
    async def test_log_child_safety_incident_convenience_function(self):
        """Test convenience function for logging child safety incidents."""
        # Clear the global instance to ensure clean test
        import src.infrastructure.security.audit_logger as audit_module

        audit_module._audit_logger = None

        event_id = await log_child_safety_incident(
            child_id="convenience_child",
            incident_type="test_incident",
            description="Convenience function safety test",
        )

        assert isinstance(event_id, str)

    @pytest.mark.asyncio
    async def test_concurrent_event_logging(self, audit_logger):
        """Test concurrent event logging."""

        async def log_event(i):
            return await audit_logger.log_event(
                event_type=AuditEventType.DATA_ACCESS,
                severity=AuditSeverity.INFO,
                category=AuditCategory.DATA_PROTECTION,
                description=f"Concurrent event {i}",
            )

        # Log 10 events concurrently
        tasks = [log_event(i) for i in range(10)]
        event_ids = await asyncio.gather(*tasks)

        # All should succeed and be unique
        assert len(event_ids) == 10
        assert len(set(event_ids)) == 10  # All unique
        assert len(audit_logger.audit_entries) == 10

    @pytest.mark.asyncio
    async def test_batch_processing_simulation(self, audit_logger):
        """Test batch processing behavior."""
        # Set small batch size for testing
        audit_logger.config.batch_size = 3

        # Add events to buffer
        for i in range(5):
            await audit_logger.log_event(
                event_type=AuditEventType.DATA_ACCESS,
                severity=AuditSeverity.INFO,
                category=AuditCategory.DATA_PROTECTION,
                description=f"Batch test event {i}",
            )

        assert len(audit_logger.audit_entries) == 5

        # Simulate batch flush
        with patch.object(audit_logger, "_write_events_to_file") as mock_write:
            async with audit_logger.buffer_lock:
                if len(audit_logger.audit_entries) >= audit_logger.config.batch_size:
                    events_to_write = audit_logger.audit_entries[
                        : audit_logger.config.batch_size
                    ]
                    audit_logger.audit_entries = audit_logger.audit_entries[
                        audit_logger.config.batch_size :
                    ]
                    await audit_logger._write_events_to_file(events_to_write)

            mock_write.assert_called_once()
            # Should have written first 3 events
            written_events = mock_write.call_args[0][0]
            assert len(written_events) == 3
            # Should have 2 events remaining in buffer
            assert len(audit_logger.audit_entries) == 2

    @pytest.mark.asyncio
    async def test_comprehensive_coppa_audit_trail(self, audit_logger):
        """Test comprehensive COPPA audit trail."""
        child_id = "coppa_audit_child"
        parent_id = "coppa_audit_parent"

        # Simulate complete COPPA workflow
        events = [
            # 1. Consent request
            (
                AuditEventType.PARENTAL_CONSENT_REQUEST,
                "Parental consent requested",
            ),
            # 2. Parent verification
            (AuditEventType.LOGIN_SUCCESS, "Parent authentication successful"),
            # 3. Consent granted
            (
                AuditEventType.PARENTAL_CONSENT_GRANTED,
                "Parental consent granted",
            ),
            # 4. Child interaction
            (
                AuditEventType.CHILD_INTERACTION_START,
                "Child interaction began",
            ),
            # 5. Data access
            (AuditEventType.DATA_ACCESS, "Child data accessed"),
            # 6. Data retention trigger
            (
                AuditEventType.DATA_RETENTION_TRIGGERED,
                "Data retention policy applied",
            ),
        ]

        event_ids = []
        for event_type, description in events:
            if event_type in [
                AuditEventType.PARENTAL_CONSENT_REQUEST,
                AuditEventType.PARENTAL_CONSENT_GRANTED,
                AuditEventType.DATA_RETENTION_TRIGGERED,
            ]:
                event_id = await audit_logger.log_coppa_event(
                    event_type=event_type,
                    child_id=child_id,
                    parent_id=parent_id,
                    description=description,
                )
            else:
                context = AuditContext(user_id=parent_id, child_id=child_id)
                event_id = await audit_logger.log_event(
                    event_type=event_type,
                    severity=AuditSeverity.INFO,
                    category=AuditCategory.COPPA_COMPLIANCE,
                    description=description,
                    context=context,
                )
            event_ids.append(event_id)

        # Verify all events logged
        assert len(audit_logger.audit_entries) == 6
        assert len(set(event_ids)) == 6  # All unique

        # Verify COPPA-related events have proper context
        coppa_events = [
            e
            for e in audit_logger.audit_entries
            if e.context and e.context.child_id == child_id
        ]
        assert len(coppa_events) >= 4

    def test_audit_event_serialization_edge_cases(self):
        """Test audit event serialization with edge cases."""
        # Test with None values
        event = AuditEvent(
            event_id="edge_case",
            timestamp=datetime.utcnow(),
            event_type=AuditEventType.SYSTEM_STARTUP,
            severity=AuditSeverity.INFO,
            category=AuditCategory.SYSTEM_SECURITY,
            description="Edge case test",
            context=None,
            details=None,
        )

        result_dict = event.to_dict()
        assert result_dict["context"] is None
        assert result_dict["details"] is None

        # Test with complex nested details
        complex_details = {
            "nested": {"level": 2, "items": [1, 2, 3]},
            "unicode": "测试",
            "boolean": True,
            "null_value": None,
        }

        event.details = complex_details
        result_dict = event.to_dict()
        assert result_dict["details"] == complex_details

    @pytest.mark.asyncio
    async def test_error_recovery_and_fallback_logging(self, audit_logger):
        """Test error recovery and fallback logging mechanisms."""
        # Test with corrupted buffer lock
        original_lock = audit_logger.buffer_lock
        audit_logger.buffer_lock = None

        # Should handle gracefully and still return event ID
        event_id = await audit_logger.log_event(
            event_type=AuditEventType.SYSTEM_STARTUP,
            severity=AuditSeverity.INFO,
            category=AuditCategory.SYSTEM_SECURITY,
            description="Error recovery test",
        )

        assert isinstance(event_id, str)

        # Restore lock
        audit_logger.buffer_lock = original_lock
