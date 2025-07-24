"""Tests for Child Data Encryption
Testing COPPA-compliant child data encryption system.
"""

import base64
import hashlib
import json
import os
from datetime import datetime, timedelta
from unittest.mock import patch

import pytest

# Mock cryptography imports for testing
pytest_plugins = ["pytest_mock"]


@pytest.fixture
def mock_cryptography(mocker):
    """Mock cryptography dependencies."""
    mock_fernet = mocker.MagicMock()
    mock_fernet.encrypt.return_value = b"encrypted_data"
    mock_fernet.decrypt.return_value = b'{"name": "Test Child"}'

    mock_fernet_class = mocker.patch(
        "src.infrastructure.security.child_data_encryption.Fernet"
    )
    mock_fernet_class.return_value = mock_fernet

    mock_pbkdf2 = mocker.patch(
        "src.infrastructure.security.child_data_encryption.PBKDF2HMAC"
    )
    mock_hashes = mocker.patch(
        "src.infrastructure.security.child_data_encryption.hashes"
    )

    return mock_fernet, mock_fernet_class, mock_pbkdf2, mock_hashes


@pytest.fixture
def mock_datetime():
    """Mock datetime for consistent testing."""
    with patch("src.infrastructure.security.child_data_encryption.datetime") as mock_dt:
        mock_dt.utcnow.return_value = datetime(2024, 1, 15, 10, 30, 0)
        yield mock_dt


try:
    from src.infrastructure.security.child_data_encryption import ChildDataEncryption
    from src.infrastructure.security.models import COPPAComplianceRecord
except ImportError:
    # Create mock classes for testing when cryptography is not available
    class ChildDataEncryption:
        SENSITIVE_FIELDS = {"name", "date_of_birth", "medical_notes"}
        PII_FIELDS = {"name", "date_of_birth", "gender"}

        def __init__(self, encryption_key=None):
            self.encryption_key = encryption_key or "test_key"
            self.data_retention_days = 90
            self.min_parent_age = 18
            self.max_child_age = 13

    class COPPAComplianceRecord:
        def __init__(self, **kwargs):
            self.child_id = kwargs.get("child_id")
            self.parental_consent_given = kwargs.get("parental_consent_given", False)
            self.consent_timestamp = kwargs.get("consent_timestamp")
            self.consent_method = kwargs.get("consent_method")
            self.consent_ip_address = kwargs.get("consent_ip_address")
            self.data_retention_expires = kwargs.get("data_retention_expires")
            self.audit_trail = kwargs.get("audit_trail", [])


class TestChildDataEncryption:
    """Test the Child Data Encryption system."""

    @pytest.fixture
    def encryption_service(self, mock_cryptography):
        """Create encryption service instance."""
        with patch.dict(os.environ, {"ENCRYPTION_KEY": "test_key_for_encryption"}):
            return ChildDataEncryption()

    def test_initialization_with_key(self, mock_cryptography):
        """Test encryption service initialization with provided key."""
        encryption_key = "custom_encryption_key"
        service = ChildDataEncryption(encryption_key=encryption_key)

        assert service.encryption_key == encryption_key
        assert service.data_retention_days == 90
        assert service.min_parent_age == 18
        assert service.max_child_age == 13

    def test_initialization_with_env_key(self, mock_cryptography):
        """Test encryption service initialization with environment key."""
        env_key = "env_encryption_key"
        with patch.dict(os.environ, {"ENCRYPTION_KEY": env_key}):
            service = ChildDataEncryption()
            assert service.encryption_key == env_key

    def test_initialization_without_key(self, mock_cryptography):
        """Test encryption service initialization without key raises error."""
        with patch.dict(os.environ, {}, clear=True):
            with pytest.raises(ValueError, match="Encryption key is required"):
                ChildDataEncryption()

    def test_sensitive_fields_definition(self):
        """Test that sensitive fields are properly defined."""
        expected_sensitive = {
            "name",
            "date_of_birth",
            "medical_notes",
            "emergency_contacts",
            "special_needs",
            "cultural_background",
            "custom_settings",
        }

        assert expected_sensitive == ChildDataEncryption.SENSITIVE_FIELDS

    def test_pii_fields_definition(self):
        """Test that PII fields are properly defined."""
        expected_pii = {
            "name",
            "date_of_birth",
            "gender",
            "emergency_contacts",
            "medical_notes",
            "cultural_background",
        }

        assert expected_pii == ChildDataEncryption.PII_FIELDS

    def test_encrypt_child_data_basic(self, encryption_service, mock_cryptography):
        """Test basic child data encryption."""
        mock_fernet, _, _, _ = mock_cryptography
        mock_fernet.encrypt.return_value = b"encrypted_sensitive_data"

        child_data = {
            "id": "child_123",
            "name": "Test Child",
            "age": 8,
            "favorite_color": "blue",
            "date_of_birth": "2016-01-15",
        }

        with patch(
            "src.infrastructure.security.child_data_encryption.datetime"
        ) as mock_dt:
            mock_dt.utcnow.return_value = datetime(2024, 1, 15, 10, 30, 0)

            result = encryption_service.encrypt_child_data(child_data)

        # Non-sensitive data should remain unchanged
        assert result["id"] == "child_123"
        assert result["age"] == 8
        assert result["favorite_color"] == "blue"

        # Sensitive data should be encrypted markers
        assert result["name"] == "[ENCRYPTED:NAME]"
        assert result["date_of_birth"] == "[ENCRYPTED:DATE_OF_BIRTH]"

        # Should contain encrypted data
        assert "_encrypted_data" in result
        assert "_encryption_metadata" in result

        # Check metadata
        metadata = result["_encryption_metadata"]
        assert metadata["encryption_version"] == "1.0"
        assert metadata["field_count"] == 2  # name and date_of_birth
        assert "checksum" in metadata

    def test_encrypt_child_data_no_sensitive_fields(self, encryption_service):
        """Test encryption when no sensitive fields are present."""
        child_data = {"id": "child_456", "age": 10, "favorite_color": "red"}

        result = encryption_service.encrypt_child_data(child_data)

        # Should return data unchanged
        assert result == child_data
        assert "_encrypted_data" not in result
        assert "_encryption_metadata" not in result

    def test_encrypt_child_data_with_none_values(
        self, encryption_service, mock_cryptography
    ):
        """Test encryption with None values in sensitive fields."""
        child_data = {
            "id": "child_789",
            "name": "Test Child",
            "date_of_birth": None,  # None value should be ignored
            "medical_notes": "",  # Empty string should be encrypted
            "age": 7,
        }

        result = encryption_service.encrypt_child_data(child_data)

        # Only non-None sensitive fields should be encrypted
        assert result["name"] == "[ENCRYPTED:NAME]"
        assert result["date_of_birth"] is None
        assert result["medical_notes"] == "[ENCRYPTED:MEDICAL_NOTES]"

        # Should have encrypted data for the two non-None sensitive fields
        assert "_encrypted_data" in result
        metadata = result["_encryption_metadata"]
        assert metadata["field_count"] == 2  # name and medical_notes

    def test_decrypt_child_data_basic(self, encryption_service, mock_cryptography):
        """Test basic child data decryption."""
        mock_fernet, _, _, _ = mock_cryptography
        mock_fernet.decrypt.return_value = json.dumps(
            {"name": "Test Child", "date_of_birth": "2016-01-15"}
        ).encode()

        encrypted_data = {
            "id": "child_123",
            "name": "[ENCRYPTED:NAME]",
            "age": 8,
            "date_of_birth": "[ENCRYPTED:DATE_OF_BIRTH]",
            "_encrypted_data": base64.b64encode(b"encrypted_data").decode(),
            "_encryption_metadata": {
                "field_count": 2,
                "checksum": "test_checksum",
            },
        }

        with patch.object(
            encryption_service,
            "_calculate_checksum",
            return_value="test_checksum",
        ):
            result = encryption_service.decrypt_child_data(encrypted_data)

        # Should have decrypted sensitive data
        assert result["name"] == "Test Child"
        assert result["date_of_birth"] == "2016-01-15"
        assert result["age"] == 8
        assert result["id"] == "child_123"

        # Encryption metadata should be removed
        assert "_encrypted_data" not in result
        assert "_encryption_metadata" not in result

    def test_decrypt_child_data_not_encrypted(self, encryption_service):
        """Test decryption of data that is not encrypted."""
        regular_data = {"id": "child_456", "age": 9, "favorite_game": "tag"}

        result = encryption_service.decrypt_child_data(regular_data)

        # Should return data unchanged
        assert result == regular_data

    def test_decrypt_child_data_integrity_check_failure(
        self, encryption_service, mock_cryptography
    ):
        """Test decryption with integrity check failure."""
        mock_fernet, _, _, _ = mock_cryptography
        mock_fernet.decrypt.return_value = json.dumps({"name": "Test Child"}).encode()

        encrypted_data = {
            "id": "child_123",
            "_encrypted_data": base64.b64encode(b"encrypted_data").decode(),
            "_encryption_metadata": {
                "field_count": 2,  # Mismatch: metadata says 2 but we only have 1
                "checksum": "wrong_checksum",
            },
        }

        with pytest.raises(ValueError, match="Data integrity check failed"):
            encryption_service.decrypt_child_data(encrypted_data)

    def test_decrypt_child_data_checksum_mismatch(
        self, encryption_service, mock_cryptography
    ):
        """Test decryption with checksum mismatch warning."""
        mock_fernet, _, _, _ = mock_cryptography
        mock_fernet.decrypt.return_value = json.dumps({"name": "Test Child"}).encode()

        encrypted_data = {
            "id": "child_123",
            "_encrypted_data": base64.b64encode(b"encrypted_data").decode(),
            "_encryption_metadata": {
                "field_count": 1,
                "checksum": "wrong_checksum",
            },
        }

        with patch.object(
            encryption_service,
            "_calculate_checksum",
            return_value="correct_checksum",
        ):
            with patch(
                "src.infrastructure.security.child_data_encryption.logger"
            ) as mock_logger:
                encryption_service.decrypt_child_data(encrypted_data)

                # Should still decrypt but log warning
                mock_logger.warning.assert_called()
                assert "integrity check failed" in mock_logger.warning.call_args[0][0]

    def test_validate_coppa_compliance_valid(self, encryption_service):
        """Test COPPA compliance validation for valid data."""
        child_data = {"age": 8}
        consent_record = COPPAComplianceRecord(
            child_id="child_123",
            parental_consent_given=True,
            consent_timestamp=datetime.utcnow(),
            consent_method="email_verification",
            consent_ip_address="192.168.1.100",
            data_retention_expires=datetime.utcnow() + timedelta(days=60),
            audit_trail=["consent_given"],
        )

        result = encryption_service.validate_coppa_compliance(
            child_data, consent_record
        )

        assert result["compliant"] is True
        assert len(result["violations"]) == 0
        assert len(result["required_actions"]) == 0

    def test_validate_coppa_compliance_age_violation(self, encryption_service):
        """Test COPPA compliance validation with age violation."""
        child_data = {"age": 15}  # Over COPPA limit
        consent_record = COPPAComplianceRecord(
            child_id="child_456", parental_consent_given=True
        )

        result = encryption_service.validate_coppa_compliance(
            child_data, consent_record
        )

        assert result["compliant"] is False
        assert len(result["violations"]) == 1
        assert "age (15) exceeds COPPA limit" in result["violations"][0]

    def test_validate_coppa_compliance_no_consent(self, encryption_service):
        """Test COPPA compliance validation without parental consent."""
        child_data = {"age": 8}
        consent_record = COPPAComplianceRecord(
            child_id="child_789", parental_consent_given=False
        )

        result = encryption_service.validate_coppa_compliance(
            child_data, consent_record
        )

        assert result["compliant"] is False
        assert "Parental consent not obtained" in result["violations"]

    def test_validate_coppa_compliance_expired_retention(self, encryption_service):
        """Test COPPA compliance validation with expired data retention."""
        child_data = {"age": 8}
        consent_record = COPPAComplianceRecord(
            child_id="child_expired",
            parental_consent_given=True,
            data_retention_expires=datetime.utcnow() - timedelta(days=1),  # Expired
        )

        result = encryption_service.validate_coppa_compliance(
            child_data, consent_record
        )

        assert result["compliant"] is False
        assert "Data retention period expired" in result["violations"]
        assert "Delete child data immediately" in result["required_actions"]

    def test_validate_coppa_compliance_pii_without_consent(self, encryption_service):
        """Test COPPA compliance validation with PII but no consent."""
        child_data = {
            "age": 8,
            "name": "Test Child",  # PII field
            "date_of_birth": "2016-01-15",  # PII field
        }
        consent_record = COPPAComplianceRecord(
            child_id="child_pii", parental_consent_given=False
        )

        result = encryption_service.validate_coppa_compliance(
            child_data, consent_record
        )

        assert result["compliant"] is False
        violations = result["violations"]
        pii_violation = [
            v for v in violations if "PII data present without consent" in v
        ]
        assert len(pii_violation) == 1
        assert "name" in pii_violation[0]
        assert "date_of_birth" in pii_violation[0]

    def test_validate_coppa_compliance_warnings(self, encryption_service):
        """Test COPPA compliance validation warnings."""
        child_data = {"age": 8}
        consent_record = COPPAComplianceRecord(
            child_id="child_warnings",
            parental_consent_given=True,
            consent_ip_address=None,  # Missing IP should trigger warning
            audit_trail=[],  # Empty audit trail should trigger warning
        )

        result = encryption_service.validate_coppa_compliance(
            child_data, consent_record
        )

        assert result["compliant"] is True  # Still compliant but with warnings
        assert len(result["warnings"]) == 2
        assert "Consent IP address not recorded" in result["warnings"]
        assert "No audit trail available" in result["warnings"]

    def test_create_consent_record(self, encryption_service, mock_datetime):
        """Test creating COPPA consent record."""
        child_id = "child_consent"
        consent_method = "government_id_verification"
        ip_address = "192.168.1.150"

        result = encryption_service.create_consent_record(
            child_id, consent_method, ip_address
        )

        assert result.child_id == child_id
        assert result.parental_consent_given is True
        assert result.consent_method == consent_method
        assert result.consent_ip_address == ip_address
        assert result.consent_timestamp == datetime(2024, 1, 15, 10, 30, 0)

        # Check data retention expiry (90 days from now)
        expected_expiry = datetime(2024, 1, 15, 10, 30, 0) + timedelta(days=90)
        assert result.data_retention_expires == expected_expiry

        # Check audit trail
        assert len(result.audit_trail) == 1
        audit_entry = result.audit_trail[0]
        assert audit_entry["action"] == "consent_given"
        assert audit_entry["method"] == consent_method
        assert audit_entry["ip_address"] == ip_address

    def test_add_audit_entry(self, encryption_service, mock_datetime):
        """Test adding audit entry to consent record."""
        consent_record = COPPAComplianceRecord(
            child_id="child_audit", parental_consent_given=True, audit_trail=[]
        )

        action = "data_accessed"
        details = {"data_type": "profile", "user_id": "parent_123"}

        encryption_service.add_audit_entry(consent_record, action, details)

        assert len(consent_record.audit_trail) == 1
        audit_entry = consent_record.audit_trail[0]
        assert audit_entry["action"] == action
        assert audit_entry["details"] == details
        assert audit_entry["timestamp"] == "2024-01-15T10:30:00"

    def test_should_delete_data_not_expired(self, encryption_service):
        """Test data deletion check for non-expired data."""
        consent_record = COPPAComplianceRecord(
            child_id="child_active",
            data_retention_expires=datetime.utcnow() + timedelta(days=30),
        )

        result = encryption_service.should_delete_data(consent_record)
        assert result is False

    def test_should_delete_data_expired(self, encryption_service):
        """Test data deletion check for expired data."""
        consent_record = COPPAComplianceRecord(
            child_id="child_expired",
            data_retention_expires=datetime.utcnow() - timedelta(days=1),
        )

        result = encryption_service.should_delete_data(consent_record)
        assert result is True

    def test_should_delete_data_no_expiry(self, encryption_service):
        """Test data deletion check when no expiry is set."""
        consent_record = COPPAComplianceRecord(
            child_id="child_no_expiry", data_retention_expires=None
        )

        result = encryption_service.should_delete_data(consent_record)
        assert result is False

    def test_anonymize_child_data(self, encryption_service, mock_datetime):
        """Test child data anonymization."""
        child_data = {
            "id": "child_anonymize",
            "name": "Test Child",
            "age": 9,
            "gender": "female",
            "date_of_birth": "2015-01-15",
            "favorite_toy": "teddy bear",
            "emergency_contacts": "parent@email.com",
        }

        result = encryption_service.anonymize_child_data(child_data)

        # Age should be converted to age group
        assert result["age"] == "elementary"

        # Gender should be preserved
        assert result["gender"] == "female"

        # PII should be anonymized
        assert result["name"] == "[ANONYMIZED]"
        assert result["date_of_birth"] == "[ANONYMIZED]"
        assert result["emergency_contacts"] == "[ANONYMIZED]"

        # Non-PII should be preserved
        assert result["favorite_toy"] == "teddy bear"

        # Should add anonymization metadata
        assert result["anonymized_at"] == "2024-01-15T10:30:00"
        assert "original_id_hash" in result

    def test_anonymize_child_data_age_groups(self, encryption_service):
        """Test age group categorization in anonymization."""
        test_cases = [
            (2, "toddler"),
            (4, "preschool"),
            (6, "early_elementary"),
            (9, "elementary"),
            (12, "preteen"),
        ]

        for age, expected_group in test_cases:
            child_data = {"age": age}
            result = encryption_service.anonymize_child_data(child_data)
            assert result["age"] == expected_group

    def test_secure_delete_child_data(self, encryption_service, mock_datetime):
        """Test secure deletion of child data."""
        child_id = "child_delete"

        result = encryption_service.secure_delete_child_data(child_id)

        assert result["child_id"] == child_id
        assert result["deleted_at"] == "2024-01-15T10:30:00"
        assert result["deletion_method"] == "secure_overwrite"
        assert result["compliance_reason"] == "COPPA_data_retention_expired"
        assert "verification_hash" in result

    def test_calculate_checksum(self, encryption_service):
        """Test checksum calculation."""
        test_data = "test data for checksum"
        result = encryption_service._calculate_checksum(test_data)

        # Should return first 16 characters of SHA256 hash
        expected = hashlib.sha256(test_data.encode("utf-8")).hexdigest()[:16]
        assert result == expected
        assert len(result) == 16

        # Same data should produce same checksum
        result2 = encryption_service._calculate_checksum(test_data)
        assert result == result2

        # Different data should produce different checksum
        result3 = encryption_service._calculate_checksum("different data")
        assert result != result3

    def test_encryption_error_handling(self, encryption_service):
        """Test error handling in encryption operations."""
        with patch.object(
            encryption_service.cipher,
            "encrypt",
            side_effect=Exception("Encryption error"),
        ):
            child_data = {"name": "Test Child"}

            with pytest.raises(ValueError, match="Child data encryption failed"):
                encryption_service.encrypt_child_data(child_data)

    def test_decryption_error_handling(self, encryption_service):
        """Test error handling in decryption operations."""
        encrypted_data = {
            "_encrypted_data": "invalid_base64",
            "_encryption_metadata": {"field_count": 1},
        }

        with pytest.raises(ValueError, match="Child data decryption failed"):
            encryption_service.decrypt_child_data(encrypted_data)

    def test_setup_encryption_cipher_fernet_key(self, mock_cryptography):
        """Test cipher setup with Fernet key format."""
        mock_fernet, mock_fernet_class, _, _ = mock_cryptography

        # Test with Fernet-formatted key (44 chars ending with =)
        fernet_key = "a" * 43 + "="

        with patch.dict(os.environ, {"ENCRYPTION_KEY": fernet_key}):
            ChildDataEncryption()

        # Should use the key directly
        mock_fernet_class.assert_called_once()

    def test_setup_encryption_cipher_custom_key(self, mock_cryptography):
        """Test cipher setup with custom key."""
        mock_fernet, mock_fernet_class, mock_pbkdf2, _ = mock_cryptography

        custom_key = "custom_encryption_key"

        with patch("base64.urlsafe_b64encode", return_value=b"derived_key"):
            with patch("os.urandom", return_value=b"salt" * 4):
                ChildDataEncryption(custom_key)

        # Should derive key using PBKDF2
        mock_pbkdf2.assert_called_once()

    def test_comprehensive_encryption_decryption_cycle(
        self, encryption_service, mock_cryptography
    ):
        """Test complete encryption-decryption cycle."""
        mock_fernet, _, _, _ = mock_cryptography

        original_data = {
            "id": "child_cycle",
            "name": "Test Child",
            "age": 7,
            "medical_notes": "No allergies",
            "favorite_color": "blue",
        }

        # Set up realistic mock responses
        sensitive_data = {
            "name": "Test Child",
            "medical_notes": "No allergies",
        }
        sensitive_json = json.dumps(sensitive_data, ensure_ascii=False, default=str)
        mock_fernet.encrypt.return_value = b"encrypted_sensitive_data"
        mock_fernet.decrypt.return_value = sensitive_json.encode()

        with patch.object(
            encryption_service,
            "_calculate_checksum",
            return_value="test_checksum",
        ):
            # Encrypt
            encrypted = encryption_service.encrypt_child_data(original_data)

            # Decrypt
            decrypted = encryption_service.decrypt_child_data(encrypted)

        # Should get back original data
        assert decrypted["id"] == original_data["id"]
        assert decrypted["name"] == original_data["name"]
        assert decrypted["age"] == original_data["age"]
        assert decrypted["medical_notes"] == original_data["medical_notes"]
        assert decrypted["favorite_color"] == original_data["favorite_color"]

    def test_coppa_compliance_comprehensive_workflow(self, encryption_service):
        """Test comprehensive COPPA compliance workflow."""
        # Step 1: Create consent record
        consent_record = encryption_service.create_consent_record(
            child_id="coppa_workflow_child",
            consent_method="email_verification",
            ip_address="192.168.1.200",
        )

        # Step 2: Add audit entries for various actions
        actions = [
            ("profile_created", {"data_type": "basic_info"}),
            ("interaction_logged", {"session_duration": 300}),
            ("data_accessed", {"accessor": "parent_123"}),
        ]

        for action, details in actions:
            encryption_service.add_audit_entry(consent_record, action, details)

        # Step 3: Validate compliance
        child_data = {
            "age": 8,
            "name": "COPPA Test Child",
            "favorite_activities": ["reading", "drawing"],
        }

        compliance_result = encryption_service.validate_coppa_compliance(
            child_data, consent_record
        )

        # Should be compliant
        assert compliance_result["compliant"] is True
        assert len(compliance_result["violations"]) == 0

        # Should have comprehensive audit trail
        assert len(consent_record.audit_trail) == 4  # 1 initial + 3 added

        # Step 4: Check data retention
        assert not encryption_service.should_delete_data(consent_record)

        # Step 5: Test anonymization
        anonymized = encryption_service.anonymize_child_data(child_data)
        assert anonymized["name"] == "[ANONYMIZED]"
        assert anonymized["age"] == "elementary"
