"""
Tests for COPPA Compliance Service
Testing COPPA compliance service functionality for child data protection.
"""

import pytest
from unittest.mock import patch, Mock
from datetime import datetime, timedelta

from src.infrastructure.security.coppa_compliance_service import (
    COPPAComplianceService,
)
from src.infrastructure.security.child_data_encryption import (
    ChildDataEncryption,
)


# Mock the COPPAComplianceRecord for testing
class MockCOPPAComplianceRecord:
    def __init__(self, **kwargs):
        self.child_id = kwargs.get("child_id")
        self.consent_timestamp = kwargs.get(
            "consent_timestamp", datetime.utcnow()
        )
        self.data_retention_expires = kwargs.get("data_retention_expires")
        self.consent_method = kwargs.get("consent_method")
        self.consent_ip_address = kwargs.get("consent_ip_address")
        self.audit_trail = kwargs.get("audit_trail", [])


class TestCOPPAComplianceService:
    """Test the COPPA Compliance Service."""

    @pytest.fixture
    def mock_encryption_service(self):
        """Create a mock encryption service."""
        mock_service = Mock(spec=ChildDataEncryption)

        # Mock create_consent_record
        mock_record = MockCOPPAComplianceRecord(
            child_id="test_child",
            consent_timestamp=datetime.utcnow(),
            data_retention_expires=datetime.utcnow() + timedelta(days=90),
        )
        mock_service.create_consent_record.return_value = mock_record

        # Mock add_audit_entry
        mock_service.add_audit_entry.return_value = None

        # Mock should_delete_data
        mock_service.should_delete_data.return_value = False

        return mock_service

    @pytest.fixture
    def coppa_service(self, mock_encryption_service):
        """Create a COPPA compliance service instance."""
        return COPPAComplianceService(mock_encryption_service)

    def test_initialization(self, coppa_service, mock_encryption_service):
        """Test COPPA compliance service initialization."""
        assert isinstance(coppa_service, COPPAComplianceService)
        assert coppa_service.encryption == mock_encryption_service
        assert hasattr(coppa_service, "consent_records")
        assert isinstance(coppa_service.consent_records, dict)
        assert len(coppa_service.consent_records) == 0

    def test_process_parental_consent_success(
        self, coppa_service, mock_encryption_service
    ):
        """Test successful parental consent processing."""
        child_id = "child_123"
        parent_email = "parent@example.com"
        consent_method = "email_verification"
        ip_address = "192.168.1.100"

        # Setup mock return value
        mock_record = MockCOPPAComplianceRecord(
            child_id=child_id,
            consent_timestamp=datetime(2024, 1, 15, 10, 30, 0),
            data_retention_expires=datetime(2024, 4, 15, 10, 30, 0),
            consent_method=consent_method,
            consent_ip_address=ip_address,
        )
        mock_encryption_service.create_consent_record.return_value = (
            mock_record
        )

        result = coppa_service.process_parental_consent(
            child_id, parent_email, consent_method, ip_address
        )

        # Verify result
        assert result["success"] is True
        assert result["child_id"] == child_id
        assert result["consent_timestamp"] == "2024-01-15T10:30:00"
        assert result["data_retention_expires"] == "2024-04-15T10:30:00"
        assert result["compliance_status"] == "compliant"

        # Verify encryption service was called correctly
        mock_encryption_service.create_consent_record.assert_called_once_with(
            child_id=child_id,
            consent_method=consent_method,
            ip_address=ip_address,
        )

        # Verify audit entry was added
        mock_encryption_service.add_audit_entry.assert_called_once()
        audit_call_args = mock_encryption_service.add_audit_entry.call_args
        assert audit_call_args[0][0] == mock_record  # consent_record
        assert audit_call_args[0][1] == "parental_consent_processed"  # action
        audit_details = audit_call_args[0][2]
        assert audit_details["parent_email"] == parent_email
        assert audit_details["method"] == consent_method

        # Verify consent record was stored
        assert child_id in coppa_service.consent_records
        assert coppa_service.consent_records[child_id] == mock_record

    def test_process_parental_consent_different_methods(
        self, coppa_service, mock_encryption_service
    ):
        """Test parental consent processing with different verification methods."""
        test_cases = [
            {
                "child_id": "child_email",
                "parent_email": "parent1@example.com",
                "consent_method": "email_verification",
                "ip_address": "192.168.1.101",
            },
            {
                "child_id": "child_sms",
                "parent_email": "parent2@example.com",
                "consent_method": "sms_verification",
                "ip_address": "192.168.1.102",
            },
            {
                "child_id": "child_gov_id",
                "parent_email": "parent3@example.com",
                "consent_method": "government_id_verification",
                "ip_address": "192.168.1.103",
            },
            {
                "child_id": "child_video",
                "parent_email": "parent4@example.com",
                "consent_method": "video_call_verification",
                "ip_address": "192.168.1.104",
            },
        ]

        for case in test_cases:
            # Reset mock for each test case
            mock_encryption_service.reset_mock()

            mock_record = MockCOPPAComplianceRecord(
                child_id=case["child_id"],
                consent_timestamp=datetime.utcnow(),
                data_retention_expires=datetime.utcnow() + timedelta(days=90),
                consent_method=case["consent_method"],
            )
            mock_encryption_service.create_consent_record.return_value = (
                mock_record
            )

            result = coppa_service.process_parental_consent(
                case["child_id"],
                case["parent_email"],
                case["consent_method"],
                case["ip_address"],
            )

            assert result["success"] is True
            assert result["child_id"] == case["child_id"]
            assert result["compliance_status"] == "compliant"

            # Verify correct method was recorded
            mock_encryption_service.create_consent_record.assert_called_once_with(
                child_id=case["child_id"],
                consent_method=case["consent_method"],
                ip_address=case["ip_address"],
            )

    def test_process_parental_consent_error_handling(
        self, coppa_service, mock_encryption_service
    ):
        """Test error handling in parental consent processing."""
        child_id = "child_error"
        parent_email = "error@example.com"
        consent_method = "email_verification"
        ip_address = "192.168.1.200"

        # Setup mock to raise exception
        mock_encryption_service.create_consent_record.side_effect = Exception(
            "Encryption service error"
        )

        result = coppa_service.process_parental_consent(
            child_id, parent_email, consent_method, ip_address
        )

        # Verify error handling
        assert result["success"] is False
        assert "error" in result
        assert "Encryption service error" in result["error"]

        # Verify no consent record was stored
        assert child_id not in coppa_service.consent_records

    def test_process_parental_consent_logging_on_error(
        self, coppa_service, mock_encryption_service
    ):
        """Test that errors are properly logged."""
        child_id = "child_log_error"
        parent_email = "log_error@example.com"
        consent_method = "sms_verification"
        ip_address = "192.168.1.201"

        # Setup mock to raise exception
        error_message = "Test encryption error"
        mock_encryption_service.create_consent_record.side_effect = Exception(
            error_message
        )

        with patch(
            "src.infrastructure.security.coppa_compliance_service.logger"
        ) as mock_logger:
            result = coppa_service.process_parental_consent(
                child_id, parent_email, consent_method, ip_address
            )

            # Verify error was logged
            mock_logger.error.assert_called_once()
            log_call = mock_logger.error.call_args[0][0]
            assert "Failed to process parental consent" in log_call
            assert error_message in str(mock_logger.error.call_args)

    def test_check_data_retention_compliance_no_expired_records(
        self, coppa_service, mock_encryption_service
    ):
        """Test data retention compliance check with no expired records."""
        # Add some active consent records
        active_records = [
            ("child_1", datetime.utcnow() + timedelta(days=30)),
            ("child_2", datetime.utcnow() + timedelta(days=60)),
            ("child_3", datetime.utcnow() + timedelta(days=90)),
        ]

        for child_id, expiry_date in active_records:
            mock_record = MockCOPPAComplianceRecord(
                child_id=child_id, data_retention_expires=expiry_date
            )
            coppa_service.consent_records[child_id] = mock_record

        # Mock should_delete_data to return False for all records
        mock_encryption_service.should_delete_data.return_value = False

        result = coppa_service.check_data_retention_compliance()

        # Should return empty list (no expired records)
        assert isinstance(result, list)
        assert len(result) == 0

        # Verify should_delete_data was called for each record
        assert mock_encryption_service.should_delete_data.call_count == 3

    def test_check_data_retention_compliance_with_expired_records(
        self, coppa_service, mock_encryption_service
    ):
        """Test data retention compliance check with expired records."""
        # Add mixed active and expired records
        now = datetime.utcnow()
        records = [
            ("child_active", now + timedelta(days=30), False),  # Active
            ("child_expired_1", now - timedelta(days=1), True),  # Expired
            ("child_active_2", now + timedelta(days=60), False),  # Active
            ("child_expired_2", now - timedelta(days=5), True),  # Expired
        ]

        for child_id, expiry_date, should_delete in records:
            mock_record = MockCOPPAComplianceRecord(
                child_id=child_id, data_retention_expires=expiry_date
            )
            coppa_service.consent_records[child_id] = mock_record

        # Mock should_delete_data to return appropriate values
        def mock_should_delete(record):
            return record.child_id in ["child_expired_1", "child_expired_2"]

        mock_encryption_service.should_delete_data.side_effect = (
            mock_should_delete
        )

        result = coppa_service.check_data_retention_compliance()

        # Should return expired records only
        assert len(result) == 2

        expired_child_ids = [record["child_id"] for record in result]
        assert "child_expired_1" in expired_child_ids
        assert "child_expired_2" in expired_child_ids

        # Verify structure of expired record entries
        for record in result:
            assert "child_id" in record
            assert "expired_at" in record
            assert "action_required" in record
            assert record["action_required"] == "delete_data"

            # Verify expired_at is properly formatted ISO string
            expired_at = record["expired_at"]
            assert isinstance(expired_at, str)
            # Should be able to parse back to datetime
            datetime.fromisoformat(expired_at)

    def test_check_data_retention_compliance_empty_records(
        self, coppa_service
    ):
        """Test data retention compliance check with no consent records."""
        result = coppa_service.check_data_retention_compliance()

        assert isinstance(result, list)
        assert len(result) == 0

    def test_check_data_retention_compliance_formatting(
        self, coppa_service, mock_encryption_service
    ):
        """Test proper formatting of expired records in compliance check."""
        # Add an expired record with specific datetime
        expired_datetime = datetime(2024, 1, 1, 12, 0, 0)
        mock_record = MockCOPPAComplianceRecord(
            child_id="child_format_test",
            data_retention_expires=expired_datetime,
        )
        coppa_service.consent_records["child_format_test"] = mock_record

        # Mock should_delete_data to return True
        mock_encryption_service.should_delete_data.return_value = True

        result = coppa_service.check_data_retention_compliance()

        assert len(result) == 1
        expired_record = result[0]

        # Verify exact formatting
        assert expired_record["child_id"] == "child_format_test"
        assert expired_record["expired_at"] == "2024-01-01T12:00:00"
        assert expired_record["action_required"] == "delete_data"

    def test_multiple_consent_records_management(
        self, coppa_service, mock_encryption_service
    ):
        """Test management of multiple consent records."""
        children_data = [
            (
                "child_1",
                "parent1@email.com",
                "email_verification",
                "192.168.1.1",
            ),
            (
                "child_2",
                "parent2@email.com",
                "sms_verification",
                "192.168.1.2",
            ),
            ("child_3", "parent3@email.com", "government_id", "192.168.1.3"),
        ]

        # Process consent for multiple children
        for child_id, parent_email, method, ip in children_data:
            mock_record = MockCOPPAComplianceRecord(
                child_id=child_id,
                consent_timestamp=datetime.utcnow(),
                data_retention_expires=datetime.utcnow() + timedelta(days=90),
            )
            mock_encryption_service.create_consent_record.return_value = (
                mock_record
            )

            result = coppa_service.process_parental_consent(
                child_id, parent_email, method, ip
            )

            assert result["success"] is True

        # Verify all records are stored
        assert len(coppa_service.consent_records) == 3
        assert "child_1" in coppa_service.consent_records
        assert "child_2" in coppa_service.consent_records
        assert "child_3" in coppa_service.consent_records

        # Verify each record has correct child_id
        for child_id in ["child_1", "child_2", "child_3"]:
            record = coppa_service.consent_records[child_id]
            assert record.child_id == child_id

    def test_consent_record_overwriting(
        self, coppa_service, mock_encryption_service
    ):
        """Test that new consent overwrites existing consent for same child."""
        child_id = "child_overwrite"

        # First consent
        mock_record_1 = MockCOPPAComplianceRecord(
            child_id=child_id,
            consent_timestamp=datetime(2024, 1, 1, 10, 0, 0),
            consent_method="email_verification",
        )
        mock_encryption_service.create_consent_record.return_value = (
            mock_record_1
        )

        result_1 = coppa_service.process_parental_consent(
            child_id, "parent@email.com", "email_verification", "192.168.1.1"
        )

        assert result_1["success"] is True
        assert coppa_service.consent_records[child_id] == mock_record_1

        # Second consent (should overwrite)
        mock_record_2 = MockCOPPAComplianceRecord(
            child_id=child_id,
            consent_timestamp=datetime(2024, 1, 2, 10, 0, 0),
            consent_method="sms_verification",
        )
        mock_encryption_service.create_consent_record.return_value = (
            mock_record_2
        )

        result_2 = coppa_service.process_parental_consent(
            child_id, "parent@email.com", "sms_verification", "192.168.1.2"
        )

        assert result_2["success"] is True
        assert coppa_service.consent_records[child_id] == mock_record_2
        assert len(coppa_service.consent_records) == 1  # Still only one record

    def test_audit_trail_integration(
        self, coppa_service, mock_encryption_service
    ):
        """Test integration with audit trail functionality."""
        child_id = "child_audit"
        parent_email = "audit@email.com"
        consent_method = "government_id_verification"
        ip_address = "192.168.1.250"

        mock_record = MockCOPPAComplianceRecord(
            child_id=child_id,
            consent_timestamp=datetime.utcnow(),
            data_retention_expires=datetime.utcnow() + timedelta(days=90),
        )
        mock_encryption_service.create_consent_record.return_value = (
            mock_record
        )

        result = coppa_service.process_parental_consent(
            child_id, parent_email, consent_method, ip_address
        )

        assert result["success"] is True

        # Verify audit entry was added with correct parameters
        mock_encryption_service.add_audit_entry.assert_called_once()
        call_args = mock_encryption_service.add_audit_entry.call_args

        # Check consent record parameter
        assert call_args[0][0] == mock_record

        # Check action parameter
        assert call_args[0][1] == "parental_consent_processed"

        # Check details parameter
        details = call_args[0][2]
        assert details["parent_email"] == parent_email
        assert details["method"] == consent_method

    def test_compliance_service_with_edge_case_data(
        self, coppa_service, mock_encryption_service
    ):
        """Test compliance service with edge case data."""
        edge_cases = [
            {
                "child_id": "",  # Empty child ID
                "parent_email": "",  # Empty email
                "consent_method": "",  # Empty method
                "ip_address": "",  # Empty IP
            },
            {
                "child_id": "child_unicode_测试",  # Unicode characters
                "parent_email": "unicode@测试.com",
                "consent_method": "email_verification",
                "ip_address": "192.168.1.100",
            },
            {
                "child_id": "child_long_" + "x" * 100,  # Very long ID
                "parent_email": "long@" + "x" * 50 + ".com",
                "consent_method": "video_call_verification",
                "ip_address": "255.255.255.255",
            },
        ]

        for i, case in enumerate(edge_cases):
            mock_record = MockCOPPAComplianceRecord(
                child_id=case["child_id"],
                consent_timestamp=datetime.utcnow(),
                data_retention_expires=datetime.utcnow() + timedelta(days=90),
            )
            mock_encryption_service.create_consent_record.return_value = (
                mock_record
            )

            try:
                result = coppa_service.process_parental_consent(
                    case["child_id"],
                    case["parent_email"],
                    case["consent_method"],
                    case["ip_address"],
                )

                # Should handle edge cases gracefully
                assert result["success"] is True
                assert result["child_id"] == case["child_id"]

            except Exception as e:
                # If encryption service rejects edge case, should handle
                # gracefully
                assert "error" in str(e).lower() or result["success"] is False

    def test_service_state_isolation(self):
        """Test that different service instances have isolated state."""
        mock_encryption_1 = Mock(spec=ChildDataEncryption)
        mock_encryption_2 = Mock(spec=ChildDataEncryption)

        service_1 = COPPAComplianceService(mock_encryption_1)
        service_2 = COPPAComplianceService(mock_encryption_2)

        # Add record to first service
        mock_record_1 = MockCOPPAComplianceRecord(child_id="child_1")
        service_1.consent_records["child_1"] = mock_record_1

        # Add record to second service
        mock_record_2 = MockCOPPAComplianceRecord(child_id="child_2")
        service_2.consent_records["child_2"] = mock_record_2

        # Verify isolation
        assert "child_1" in service_1.consent_records
        assert "child_1" not in service_2.consent_records
        assert "child_2" in service_2.consent_records
        assert "child_2" not in service_1.consent_records

        assert len(service_1.consent_records) == 1
        assert len(service_2.consent_records) == 1
