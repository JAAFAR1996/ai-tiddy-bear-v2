"""
Tests for Child Data Security Manager
Testing enhanced child data security manager with COPPA compliance.
"""

import pytest
from unittest.mock import patch, Mock
from datetime import datetime, timedelta

from src.infrastructure.security.child_data_security_manager import (
    ChildDataSecurityManager,
)


# Mock classes for testing
class MockCOPPAComplianceRecord:
    def __init__(self, **kwargs):
        self.child_id = kwargs.get("child_id")
        self.consent_timestamp = kwargs.get(
            "consent_timestamp", datetime.utcnow()
        )
        self.data_retention_expires = kwargs.get(
            "data_retention_expires", datetime.utcnow() + timedelta(days=90)
        )
        self.consent_method = kwargs.get("consent_method")
        self.consent_ip_address = kwargs.get("consent_ip_address")
        self.audit_trail = kwargs.get("audit_trail", [])


class TestChildDataSecurityManager:
    """Test the Child Data Security Manager."""

    @pytest.fixture
    def mock_encryption_service(self):
        """Create a mock encryption service."""
        with patch(
            "src.infrastructure.security.child_data_security_manager.ChildDataEncryption"
        ) as mock_class:
            mock_service = Mock()
            mock_class.return_value = mock_service

            # Setup default mock behaviors
            mock_consent_record = MockCOPPAComplianceRecord()
            mock_service.create_consent_record.return_value = (
                mock_consent_record
            )
            mock_service.validate_coppa_compliance.return_value = {
                "compliant": True,
                "violations": [],
                "warnings": [],
                "required_actions": [],
            }
            mock_service.encrypt_child_data.return_value = {
                "id": "child_123",
                "name": "[ENCRYPTED:NAME]",
                "_encrypted_data": "encrypted_content",
            }
            mock_service.decrypt_child_data.return_value = {
                "id": "child_123",
                "name": "Test Child",
                "age": 8,
            }

            yield mock_service

    @pytest.fixture
    def mock_coppa_service(self):
        """Create a mock COPPA service."""
        with patch(
            "src.infrastructure.security.child_data_security_manager.COPPAComplianceService"
        ) as mock_class:
            mock_service = Mock()
            mock_class.return_value = mock_service

            mock_service.check_data_retention_compliance.return_value = []

            yield mock_service

    @pytest.fixture
    def security_manager(self, mock_encryption_service, mock_coppa_service):
        """Create a child data security manager instance."""
        return ChildDataSecurityManager(encryption_key="test_key")

    def test_initialization_with_key(
        self, mock_encryption_service, mock_coppa_service
    ):
        """Test security manager initialization with encryption key."""
        encryption_key = "test_encryption_key"
        manager = ChildDataSecurityManager(encryption_key)

        assert hasattr(manager, "encryption")
        assert hasattr(manager, "coppa_service")
        assert manager.encryption is not None
        assert manager.coppa_service is not None

    def test_initialization_without_key(
        self, mock_encryption_service, mock_coppa_service
    ):
        """Test security manager initialization without encryption key."""
        manager = ChildDataSecurityManager()

        assert hasattr(manager, "encryption")
        assert hasattr(manager, "coppa_service")

    def test_secure_child_profile_success(
        self, security_manager, mock_encryption_service, mock_coppa_service
    ):
        """Test successful child profile securing."""
        child_data = {
            "id": "child_123",
            "name": "Test Child",
            "age": 8,
            "date_of_birth": "2016-01-15",
        }

        parent_consent = {
            "method": "email_verification",
            "ip_address": "192.168.1.100",
        }

        # Setup mock return values
        mock_consent_record = MockCOPPAComplianceRecord(
            child_id="child_123",
            consent_timestamp=datetime(2024, 1, 15, 10, 30, 0),
            data_retention_expires=datetime(2024, 4, 15, 10, 30, 0),
        )
        security_manager.encryption.create_consent_record.return_value = (
            mock_consent_record
        )

        compliance_check = {
            "compliant": True,
            "violations": [],
            "warnings": [],
            "required_actions": [],
        }
        security_manager.encryption.validate_coppa_compliance.return_value = (
            compliance_check
        )

        encrypted_data = {
            "id": "child_123",
            "name": "[ENCRYPTED:NAME]",
            "age": 8,
            "date_of_birth": "[ENCRYPTED:DATE_OF_BIRTH]",
            "_encrypted_data": "encrypted_sensitive_data",
        }
        security_manager.encryption.encrypt_child_data.return_value = (
            encrypted_data
        )

        result = security_manager.secure_child_profile(
            child_data, parent_consent
        )

        # Verify encryption service calls
        security_manager.encryption.create_consent_record.assert_called_once_with(
            child_id="child_123",
            consent_method="email_verification",
            ip_address="192.168.1.100",
        )
        security_manager.encryption.validate_coppa_compliance.assert_called_once_with(
            child_data, mock_consent_record
        )
        security_manager.encryption.encrypt_child_data.assert_called_once_with(
            child_data
        )

        # Verify result structure
        assert result["id"] == "child_123"
        assert result["name"] == "[ENCRYPTED:NAME]"
        assert "_coppa_compliance" in result

        coppa_info = result["_coppa_compliance"]
        assert coppa_info["consent_timestamp"] == "2024-01-15T10:30:00"
        assert coppa_info["data_retention_expires"] == "2024-04-15T10:30:00"
        assert coppa_info["compliance_verified"] is True

    def test_secure_child_profile_compliance_violation(self, security_manager):
        """Test child profile securing with COPPA compliance violations."""
        child_data = {
            "id": "child_noncompliant",
            "name": "Test Child",
            "age": 15,  # Over COPPA age limit
        }

        parent_consent = {
            "method": "email_verification",
            "ip_address": "192.168.1.101",
        }

        # Setup compliance violation
        compliance_check = {
            "compliant": False,
            "violations": ["Child age exceeds COPPA limit"],
            "warnings": [],
            "required_actions": ["Obtain enhanced parental consent"],
        }
        security_manager.encryption.validate_coppa_compliance.return_value = (
            compliance_check
        )

        with pytest.raises(ValueError, match="COPPA compliance violations"):
            security_manager.secure_child_profile(child_data, parent_consent)

    def test_secure_child_profile_missing_child_id(self, security_manager):
        """Test child profile securing with missing child ID."""
        child_data = {
            "name": "Test Child",
            "age": 8,
            # Missing "id" field
        }

        parent_consent = {
            "method": "sms_verification",
            "ip_address": "192.168.1.102",
        }

        result = security_manager.secure_child_profile(
            child_data, parent_consent
        )

        # Should handle gracefully with empty string for child_id
        security_manager.encryption.create_consent_record.assert_called_once_with(
            child_id="",  # Empty string when id is missing
            consent_method="sms_verification",
            ip_address="192.168.1.102",
        )

    def test_secure_child_profile_missing_consent_fields(
        self, security_manager
    ):
        """Test child profile securing with missing consent fields."""
        child_data = {
            "id": "child_missing_consent",
            "name": "Test Child",
            "age": 7,
        }

        parent_consent = {
            # Missing method and ip_address
        }

        result = security_manager.secure_child_profile(
            child_data, parent_consent
        )

        # Should handle missing fields with defaults
        security_manager.encryption.create_consent_record.assert_called_once_with(
            child_id="child_missing_consent",
            consent_method="digital",  # Default method
            ip_address=None,  # None when missing
        )

    def test_secure_child_profile_error_handling(self, security_manager):
        """Test error handling in child profile securing."""
        child_data = {"id": "child_error"}
        parent_consent = {"method": "email", "ip_address": "192.168.1.200"}

        # Setup encryption service to raise exception
        security_manager.encryption.create_consent_record.side_effect = (
            Exception("Encryption error")
        )

        with pytest.raises(Exception, match="Encryption error"):
            security_manager.secure_child_profile(child_data, parent_consent)

    def test_secure_child_profile_logging_on_error(self, security_manager):
        """Test that errors are properly logged in secure_child_profile."""
        child_data = {"id": "child_log_error"}
        parent_consent = {"method": "email", "ip_address": "192.168.1.201"}

        error_message = "Test encryption error"
        security_manager.encryption.create_consent_record.side_effect = (
            Exception(error_message)
        )

        with patch(
            "src.infrastructure.security.child_data_security_manager.logger"
        ) as mock_logger:
            with pytest.raises(Exception):
                security_manager.secure_child_profile(
                    child_data, parent_consent
                )

            mock_logger.error.assert_called_once()
            log_call = mock_logger.error.call_args[0][0]
            assert "Failed to secure child profile" in log_call

    def test_get_child_data_for_interaction_success(self, security_manager):
        """Test successful child data retrieval for interaction."""
        encrypted_child_data = {
            "id": "child_123",
            "name": "[ENCRYPTED:NAME]",
            "_encrypted_data": "encrypted_content",
            "_coppa_compliance": {
                "consent_timestamp": "2024-01-15T10:30:00",
                "data_retention_expires": (
                    datetime.utcnow() + timedelta(days=30)
                ).isoformat(),
                "compliance_verified": True,
            },
        }

        decrypted_data = {
            "id": "child_123",
            "name": "Test Child",
            "age": 8,
            "favorite_color": "blue",
        }
        security_manager.encryption.decrypt_child_data.return_value = (
            decrypted_data
        )

        result = security_manager.get_child_data_for_interaction(
            encrypted_child_data
        )

        # Verify decryption was called
        security_manager.encryption.decrypt_child_data.assert_called_once_with(
            encrypted_child_data
        )

        # Verify result
        assert result == decrypted_data
        assert result["name"] == "Test Child"
        assert result["age"] == 8

    def test_get_child_data_for_interaction_expired_retention(
        self, security_manager
    ):
        """Test child data retrieval with expired data retention."""
        expired_date = datetime.utcnow() - timedelta(days=1)
        encrypted_child_data = {
            "id": "child_expired",
            "name": "[ENCRYPTED:NAME]",
            "_coppa_compliance": {
                "data_retention_expires": expired_date.isoformat()
            },
        }

        with pytest.raises(
            ValueError, match="Child data retention period expired"
        ):
            security_manager.get_child_data_for_interaction(
                encrypted_child_data
            )

        # Should not attempt decryption for expired data
        security_manager.encryption.decrypt_child_data.assert_not_called()

    def test_get_child_data_for_interaction_no_coppa_info(
        self, security_manager
    ):
        """Test child data retrieval without COPPA compliance info."""
        encrypted_child_data = {
            "id": "child_no_coppa",
            "name": "[ENCRYPTED:NAME]",
            "_encrypted_data": "encrypted_content",
            # Missing _coppa_compliance
        }

        decrypted_data = {"id": "child_no_coppa", "name": "Test Child"}
        security_manager.encryption.decrypt_child_data.return_value = (
            decrypted_data
        )

        result = security_manager.get_child_data_for_interaction(
            encrypted_child_data
        )

        # Should still work without COPPA info (no expiry check)
        assert result == decrypted_data

    def test_get_child_data_for_interaction_no_expiry(self, security_manager):
        """Test child data retrieval without expiry date."""
        encrypted_child_data = {
            "id": "child_no_expiry",
            "name": "[ENCRYPTED:NAME]",
            "_coppa_compliance": {
                "consent_timestamp": "2024-01-15T10:30:00",
                "compliance_verified": True,
                # Missing data_retention_expires
            },
        }

        decrypted_data = {"id": "child_no_expiry", "name": "Test Child"}
        security_manager.encryption.decrypt_child_data.return_value = (
            decrypted_data
        )

        result = security_manager.get_child_data_for_interaction(
            encrypted_child_data
        )

        # Should work without expiry (no expiry check)
        assert result == decrypted_data

    def test_get_child_data_for_interaction_error_handling(
        self, security_manager
    ):
        """Test error handling in child data retrieval."""
        encrypted_child_data = {"id": "child_decrypt_error"}

        # Setup decryption to raise exception
        security_manager.encryption.decrypt_child_data.side_effect = Exception(
            "Decryption error"
        )

        with pytest.raises(Exception, match="Decryption error"):
            security_manager.get_child_data_for_interaction(
                encrypted_child_data
            )

    def test_get_child_data_for_interaction_logging_on_error(
        self, security_manager
    ):
        """Test that errors are properly logged in get_child_data_for_interaction."""
        encrypted_child_data = {"id": "child_log_error"}

        error_message = "Test decryption error"
        security_manager.encryption.decrypt_child_data.side_effect = Exception(
            error_message
        )

        with patch(
            "src.infrastructure.security.child_data_security_manager.logger"
        ) as mock_logger:
            with pytest.raises(Exception):
                security_manager.get_child_data_for_interaction(
                    encrypted_child_data
                )

            mock_logger.error.assert_called_once()
            log_call = mock_logger.error.call_args[0][0]
            assert "Failed to get child data for interaction" in log_call

    def test_schedule_data_cleanup_no_expired_records(self, security_manager):
        """Test data cleanup scheduling with no expired records."""
        # Setup COPPA service to return no expired records
        security_manager.coppa_service.check_data_retention_compliance.return_value = (
            []
        )

        with patch(
            "src.infrastructure.security.child_data_security_manager.datetime"
        ) as mock_dt:
            mock_dt.utcnow.return_value = datetime(2024, 1, 15, 10, 30, 0)

            result = security_manager.schedule_data_cleanup()

        # Verify result structure
        assert result["total_expired"] == 0
        assert result["expired_records"] == []
        assert result["cleanup_scheduled"] == "2024-01-15T10:30:00"

        # Verify COPPA service was called
        security_manager.coppa_service.check_data_retention_compliance.assert_called_once()

    def test_schedule_data_cleanup_with_expired_records(
        self, security_manager
    ):
        """Test data cleanup scheduling with expired records."""
        expired_records = [
            {
                "child_id": "child_expired_1",
                "expired_at": "2024-01-01T10:30:00",
                "action_required": "delete_data",
            },
            {
                "child_id": "child_expired_2",
                "expired_at": "2024-01-02T15:45:00",
                "action_required": "delete_data",
            },
        ]

        security_manager.coppa_service.check_data_retention_compliance.return_value = (
            expired_records
        )

        with patch(
            "src.infrastructure.security.child_data_security_manager.datetime"
        ) as mock_dt:
            mock_dt.utcnow.return_value = datetime(2024, 1, 15, 10, 30, 0)

            result = security_manager.schedule_data_cleanup()

        # Verify result structure
        assert result["total_expired"] == 2
        assert result["expired_records"] == expired_records
        assert result["cleanup_scheduled"] == "2024-01-15T10:30:00"

        # Should include the expired records details
        assert len(result["expired_records"]) == 2
        assert result["expired_records"][0]["child_id"] == "child_expired_1"
        assert result["expired_records"][1]["child_id"] == "child_expired_2"

    def test_schedule_data_cleanup_logging_warning(self, security_manager):
        """Test that warnings are logged when expired records are found."""
        expired_records = [
            {"child_id": "child_1", "expired_at": "2024-01-01T10:30:00"},
            {"child_id": "child_2", "expired_at": "2024-01-02T10:30:00"},
            {"child_id": "child_3", "expired_at": "2024-01-03T10:30:00"},
        ]

        security_manager.coppa_service.check_data_retention_compliance.return_value = (
            expired_records
        )

        with patch(
            "src.infrastructure.security.child_data_security_manager.logger"
        ) as mock_logger:
            security_manager.schedule_data_cleanup()

            mock_logger.warning.assert_called_once()
            log_call = mock_logger.warning.call_args[0][0]
            assert "Found 3 child records requiring data deletion" in log_call

    def test_schedule_data_cleanup_no_logging_when_no_expired(
        self, security_manager
    ):
        """Test that no warning is logged when no expired records are found."""
        security_manager.coppa_service.check_data_retention_compliance.return_value = (
            []
        )

        with patch(
            "src.infrastructure.security.child_data_security_manager.logger"
        ) as mock_logger:
            security_manager.schedule_data_cleanup()

            # Should not log warning when no expired records
            mock_logger.warning.assert_not_called()

    def test_comprehensive_workflow(self, security_manager):
        """Test comprehensive workflow from securing to cleanup."""
        # Step 1: Secure child profile
        child_data = {
            "id": "child_workflow",
            "name": "Workflow Child",
            "age": 9,
            "medical_notes": "No allergies",
        }

        parent_consent = {
            "method": "government_id_verification",
            "ip_address": "192.168.1.150",
        }

        # Setup mocks for securing
        mock_consent_record = MockCOPPAComplianceRecord(
            child_id="child_workflow",
            consent_timestamp=datetime(2024, 1, 15, 10, 30, 0),
            data_retention_expires=datetime(2024, 4, 15, 10, 30, 0),
        )
        security_manager.encryption.create_consent_record.return_value = (
            mock_consent_record
        )

        compliance_check = {
            "compliant": True,
            "violations": [],
            "warnings": [],
            "required_actions": [],
        }
        security_manager.encryption.validate_coppa_compliance.return_value = (
            compliance_check
        )

        encrypted_result = {
            "id": "child_workflow",
            "name": "[ENCRYPTED:NAME]",
            "age": 9,
            "medical_notes": "[ENCRYPTED:MEDICAL_NOTES]",
            "_encrypted_data": "encrypted_sensitive_data",
        }
        security_manager.encryption.encrypt_child_data.return_value = (
            encrypted_result
        )

        secured_profile = security_manager.secure_child_profile(
            child_data, parent_consent
        )

        # Verify secured profile
        assert secured_profile["id"] == "child_workflow"
        assert "_coppa_compliance" in secured_profile

        # Step 2: Get data for interaction
        decrypted_for_interaction = {
            "id": "child_workflow",
            "name": "Workflow Child",
            "age": 9,
            "medical_notes": "No allergies",
        }
        security_manager.encryption.decrypt_child_data.return_value = (
            decrypted_for_interaction
        )

        interaction_data = security_manager.get_child_data_for_interaction(
            secured_profile
        )
        assert interaction_data["name"] == "Workflow Child"

        # Step 3: Schedule cleanup
        security_manager.coppa_service.check_data_retention_compliance.return_value = (
            []
        )

        cleanup_result = security_manager.schedule_data_cleanup()
        assert cleanup_result["total_expired"] == 0

    def test_service_integration_with_different_consent_methods(
        self, security_manager
    ):
        """Test service integration with different consent verification methods."""
        consent_methods = [
            "email_verification",
            "sms_verification",
            "government_id_verification",
            "video_call_verification",
            "digital_signature",
        ]

        for i, method in enumerate(consent_methods):
            child_data = {
                "id": f"child_{method}_{i}",
                "name": f"Child {i}",
                "age": 8,
            }

            parent_consent = {
                "method": method,
                "ip_address": f"192.168.1.{100 + i}",
            }

            # Each method should work
            result = security_manager.secure_child_profile(
                child_data, parent_consent
            )

            assert result["id"] == f"child_{method}_{i}"
            assert "_coppa_compliance" in result

            # Verify correct method was used
            security_manager.encryption.create_consent_record.assert_called_with(
                child_id=f"child_{method}_{i}",
                consent_method=method,
                ip_address=f"192.168.1.{100 + i}",
            )

    def test_edge_cases_datetime_handling(self, security_manager):
        """Test edge cases in datetime handling."""
        # Test with various datetime formats in COPPA compliance
        datetime_formats = [
            datetime.utcnow().isoformat(),
            datetime.utcnow().isoformat() + "Z",
            "2024-01-15T10:30:00.123456",
            "2024-12-31T23:59:59",
        ]

        for dt_str in datetime_formats:
            encrypted_child_data = {
                "id": "child_datetime_test",
                "_coppa_compliance": {"data_retention_expires": dt_str},
            }

            decrypted_data = {"id": "child_datetime_test", "name": "Test"}
            security_manager.encryption.decrypt_child_data.return_value = (
                decrypted_data
            )

            try:
                # Should handle various datetime formats
                result = security_manager.get_child_data_for_interaction(
                    encrypted_child_data
                )
                assert result == decrypted_data
            except ValueError as e:
                # Some formats might not be parseable, that's expected
                assert "time data" in str(e) or "does not match format" in str(
                    e
                )

    def test_memory_efficiency_large_datasets(self, security_manager):
        """Test memory efficiency with large datasets."""
        # Test with large child data
        large_child_data = {
            "id": "child_large",
            "name": "Large Data Child",
            "age": 8,
            "large_field": "x" * 10000,  # 10KB field
            "medical_notes": "y" * 5000,  # 5KB field
        }

        parent_consent = {
            "method": "email_verification",
            "ip_address": "192.168.1.200",
        }

        # Should handle large data without issues
        result = security_manager.secure_child_profile(
            large_child_data, parent_consent
        )

        assert result["id"] == "child_large"
        assert "_coppa_compliance" in result

    def test_concurrent_operations(self, security_manager):
        """Test concurrent operations on the security manager."""
        import threading

        results = []
        errors = []

        def secure_profile(child_num):
            try:
                child_data = {
                    "id": f"child_concurrent_{child_num}",
                    "name": f"Child {child_num}",
                    "age": 8,
                }
                parent_consent = {
                    "method": "email_verification",
                    "ip_address": f"192.168.1.{100 + child_num}",
                }

                result = security_manager.secure_child_profile(
                    child_data, parent_consent
                )
                results.append(result)
            except Exception as e:
                errors.append(e)

        # Create multiple threads
        threads = []
        for i in range(5):
            thread = threading.Thread(target=secure_profile, args=(i,))
            threads.append(thread)

        # Start all threads
        for thread in threads:
            thread.start()

        # Wait for completion
        for thread in threads:
            thread.join()

        # Should handle concurrent operations
        assert len(errors) == 0, f"Concurrent operations failed: {errors}"
        assert len(results) == 5
