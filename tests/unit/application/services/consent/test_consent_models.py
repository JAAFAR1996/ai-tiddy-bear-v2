"""Tests for Consent Models
Testing COPPA-compliant consent management data structures.
"""

from dataclasses import asdict

import pytest

from src.application.services.consent.consent_models import (
    ConsentRecord,
    VerificationAttempt,
    VerificationMethod,
    VerificationStatus,
)


class TestVerificationMethod:
    """Test the VerificationMethod enum."""

    def test_verification_method_values(self):
        """Test VerificationMethod enum values."""
        assert VerificationMethod.EMAIL_VERIFICATION == "email_verification"
        assert VerificationMethod.SMS_VERIFICATION == "sms_verification"
        assert VerificationMethod.CREDIT_CARD_VERIFICATION == "credit_card_verification"
        assert VerificationMethod.DIGITAL_SIGNATURE == "digital_signature"
        assert VerificationMethod.VIDEO_CALL_VERIFICATION == "video_call_verification"
        assert (
            VerificationMethod.GOVERNMENT_ID_VERIFICATION
            == "government_id_verification"
        )

    def test_verification_method_enum_membership(self):
        """Test that all verification methods are enum members."""
        methods = [
            VerificationMethod.EMAIL_VERIFICATION,
            VerificationMethod.SMS_VERIFICATION,
            VerificationMethod.CREDIT_CARD_VERIFICATION,
            VerificationMethod.DIGITAL_SIGNATURE,
            VerificationMethod.VIDEO_CALL_VERIFICATION,
            VerificationMethod.GOVERNMENT_ID_VERIFICATION,
        ]

        for method in methods:
            assert isinstance(method, VerificationMethod)

    def test_verification_method_string_representation(self):
        """Test string representation of verification methods."""
        assert (
            str(VerificationMethod.EMAIL_VERIFICATION)
            == "VerificationMethod.EMAIL_VERIFICATION"
        )
        assert VerificationMethod.EMAIL_VERIFICATION.value == "email_verification"


class TestVerificationStatus:
    """Test the VerificationStatus enum."""

    def test_verification_status_values(self):
        """Test VerificationStatus enum values."""
        assert VerificationStatus.PENDING == "pending"
        assert VerificationStatus.IN_PROGRESS == "in_progress"
        assert VerificationStatus.VERIFIED == "verified"
        assert VerificationStatus.FAILED == "failed"
        assert VerificationStatus.EXPIRED == "expired"

    def test_verification_status_enum_membership(self):
        """Test that all verification statuses are enum members."""
        statuses = [
            VerificationStatus.PENDING,
            VerificationStatus.IN_PROGRESS,
            VerificationStatus.VERIFIED,
            VerificationStatus.FAILED,
            VerificationStatus.EXPIRED,
        ]

        for status in statuses:
            assert isinstance(status, VerificationStatus)

    def test_verification_status_workflow_transitions(self):
        """Test logical workflow transitions between statuses."""
        # Test that we have all the expected workflow states
        workflow_states = {
            VerificationStatus.PENDING,
            VerificationStatus.IN_PROGRESS,
            VerificationStatus.VERIFIED,
            VerificationStatus.FAILED,
            VerificationStatus.EXPIRED,
        }

        assert len(workflow_states) == 5
        assert VerificationStatus.PENDING in workflow_states
        assert VerificationStatus.VERIFIED in workflow_states


class TestConsentRecord:
    """Test the ConsentRecord dataclass."""

    @pytest.fixture
    def sample_consent_record(self):
        """Create a sample consent record for testing."""
        return ConsentRecord(
            consent_id="consent_parent123_child456_feature_audio",
            parent_id="parent123",
            child_id="child456",
            feature="audio_recording",
            status="pending",
            requested_at="2024-01-15T10:30:00",
            expiry_date="2025-01-15T10:30:00",
        )

    def test_consent_record_creation_required_fields(self):
        """Test ConsentRecord creation with required fields only."""
        record = ConsentRecord(
            consent_id="test_consent_id",
            parent_id="test_parent",
            child_id="test_child",
            feature="test_feature",
            status="pending",
            requested_at="2024-01-15T10:30:00",
            expiry_date="2025-01-15T10:30:00",
        )

        assert record.consent_id == "test_consent_id"
        assert record.parent_id == "test_parent"
        assert record.child_id == "test_child"
        assert record.feature == "test_feature"
        assert record.status == "pending"
        assert record.requested_at == "2024-01-15T10:30:00"
        assert record.expiry_date == "2025-01-15T10:30:00"

        # Optional fields should be None
        assert record.granted_at is None
        assert record.revoked_at is None
        assert record.verification_method is None
        assert record.metadata is None

    def test_consent_record_creation_all_fields(self):
        """Test ConsentRecord creation with all fields."""
        metadata = {"request_source": "web", "ip_address": "192.168.1.1"}

        record = ConsentRecord(
            consent_id="full_consent_id",
            parent_id="parent789",
            child_id="child012",
            feature="personalization",
            status="granted",
            requested_at="2024-01-15T10:30:00",
            expiry_date="2025-01-15T10:30:00",
            granted_at="2024-01-15T11:00:00",
            revoked_at=None,
            verification_method="email_verification",
            metadata=metadata,
        )

        assert record.consent_id == "full_consent_id"
        assert record.parent_id == "parent789"
        assert record.child_id == "child012"
        assert record.feature == "personalization"
        assert record.status == "granted"
        assert record.granted_at == "2024-01-15T11:00:00"
        assert record.verification_method == "email_verification"
        assert record.metadata == metadata

    def test_consent_record_dataclass_behavior(self, sample_consent_record):
        """Test dataclass behavior of ConsentRecord."""
        # Test field access
        assert sample_consent_record.parent_id == "parent123"
        assert sample_consent_record.child_id == "child456"

        # Test field modification
        sample_consent_record.status = "granted"
        assert sample_consent_record.status == "granted"

        # Test dataclass conversion to dict
        record_dict = asdict(sample_consent_record)
        assert isinstance(record_dict, dict)
        assert record_dict["consent_id"] == "consent_parent123_child456_feature_audio"
        assert record_dict["parent_id"] == "parent123"

    def test_consent_record_equality(self):
        """Test ConsentRecord equality comparison."""
        record1 = ConsentRecord(
            consent_id="same_id",
            parent_id="parent1",
            child_id="child1",
            feature="feature1",
            status="pending",
            requested_at="2024-01-15T10:30:00",
            expiry_date="2025-01-15T10:30:00",
        )

        record2 = ConsentRecord(
            consent_id="same_id",
            parent_id="parent1",
            child_id="child1",
            feature="feature1",
            status="pending",
            requested_at="2024-01-15T10:30:00",
            expiry_date="2025-01-15T10:30:00",
        )

        record3 = ConsentRecord(
            consent_id="different_id",
            parent_id="parent1",
            child_id="child1",
            feature="feature1",
            status="pending",
            requested_at="2024-01-15T10:30:00",
            expiry_date="2025-01-15T10:30:00",
        )

        assert record1 == record2
        assert record1 != record3

    def test_consent_record_coppa_compliance_fields(self, sample_consent_record):
        """Test that ConsentRecord includes COPPA-required fields."""
        # COPPA requires tracking of consent details
        assert hasattr(sample_consent_record, "parent_id")
        assert hasattr(sample_consent_record, "child_id")
        assert hasattr(sample_consent_record, "feature")
        assert hasattr(sample_consent_record, "status")
        assert hasattr(sample_consent_record, "requested_at")
        assert hasattr(sample_consent_record, "expiry_date")
        assert hasattr(sample_consent_record, "granted_at")
        assert hasattr(sample_consent_record, "revoked_at")
        assert hasattr(sample_consent_record, "verification_method")

    def test_consent_record_metadata_handling(self):
        """Test metadata field handling in ConsentRecord."""
        # Test with None metadata
        record1 = ConsentRecord(
            consent_id="meta_test_1",
            parent_id="parent1",
            child_id="child1",
            feature="feature1",
            status="pending",
            requested_at="2024-01-15T10:30:00",
            expiry_date="2025-01-15T10:30:00",
            metadata=None,
        )
        assert record1.metadata is None

        # Test with empty dict metadata
        record2 = ConsentRecord(
            consent_id="meta_test_2",
            parent_id="parent1",
            child_id="child1",
            feature="feature1",
            status="pending",
            requested_at="2024-01-15T10:30:00",
            expiry_date="2025-01-15T10:30:00",
            metadata={},
        )
        assert record2.metadata == {}

        # Test with complex metadata
        complex_metadata = {
            "request_source": "mobile_app",
            "user_agent": "Mozilla/5.0...",
            "geolocation": {"country": "US", "state": "CA"},
            "compliance_notes": ["COPPA verified", "Parent confirmed"],
        }
        record3 = ConsentRecord(
            consent_id="meta_test_3",
            parent_id="parent1",
            child_id="child1",
            feature="feature1",
            status="pending",
            requested_at="2024-01-15T10:30:00",
            expiry_date="2025-01-15T10:30:00",
            metadata=complex_metadata,
        )
        assert record3.metadata == complex_metadata


class TestVerificationAttempt:
    """Test the VerificationAttempt dataclass."""

    @pytest.fixture
    def sample_verification_attempt(self):
        """Create a sample verification attempt for testing."""
        return VerificationAttempt(
            attempt_id="attempt_123",
            consent_id="consent_456",
            method=VerificationMethod.EMAIL_VERIFICATION,
            status=VerificationStatus.PENDING,
            attempted_at="2024-01-15T10:30:00",
        )

    def test_verification_attempt_creation_required_fields(self):
        """Test VerificationAttempt creation with required fields only."""
        attempt = VerificationAttempt(
            attempt_id="test_attempt",
            consent_id="test_consent",
            method=VerificationMethod.SMS_VERIFICATION,
            status=VerificationStatus.PENDING,
            attempted_at="2024-01-15T10:30:00",
        )

        assert attempt.attempt_id == "test_attempt"
        assert attempt.consent_id == "test_consent"
        assert attempt.method == VerificationMethod.SMS_VERIFICATION
        assert attempt.status == VerificationStatus.PENDING
        assert attempt.attempted_at == "2024-01-15T10:30:00"

        # Optional fields should be None
        assert attempt.completed_at is None
        assert attempt.failure_reason is None
        assert attempt.verification_code is None

    def test_verification_attempt_creation_all_fields(self):
        """Test VerificationAttempt creation with all fields."""
        attempt = VerificationAttempt(
            attempt_id="full_attempt",
            consent_id="full_consent",
            method=VerificationMethod.EMAIL_VERIFICATION,
            status=VerificationStatus.VERIFIED,
            attempted_at="2024-01-15T10:30:00",
            completed_at="2024-01-15T10:35:00",
            failure_reason=None,
            verification_code="123456",
        )

        assert attempt.attempt_id == "full_attempt"
        assert attempt.consent_id == "full_consent"
        assert attempt.method == VerificationMethod.EMAIL_VERIFICATION
        assert attempt.status == VerificationStatus.VERIFIED
        assert attempt.attempted_at == "2024-01-15T10:30:00"
        assert attempt.completed_at == "2024-01-15T10:35:00"
        assert attempt.failure_reason is None
        assert attempt.verification_code == "123456"

    def test_verification_attempt_with_failure(self):
        """Test VerificationAttempt creation for failed attempts."""
        attempt = VerificationAttempt(
            attempt_id="failed_attempt",
            consent_id="failed_consent",
            method=VerificationMethod.SMS_VERIFICATION,
            status=VerificationStatus.FAILED,
            attempted_at="2024-01-15T10:30:00",
            completed_at="2024-01-15T10:35:00",
            failure_reason="Invalid verification code",
            verification_code="654321",
        )

        assert attempt.status == VerificationStatus.FAILED
        assert attempt.failure_reason == "Invalid verification code"
        assert attempt.completed_at is not None

    def test_verification_attempt_dataclass_behavior(self, sample_verification_attempt):
        """Test dataclass behavior of VerificationAttempt."""
        # Test field access
        assert sample_verification_attempt.attempt_id == "attempt_123"
        assert (
            sample_verification_attempt.method == VerificationMethod.EMAIL_VERIFICATION
        )

        # Test field modification
        sample_verification_attempt.status = VerificationStatus.VERIFIED
        assert sample_verification_attempt.status == VerificationStatus.VERIFIED

        # Test dataclass conversion to dict
        attempt_dict = asdict(sample_verification_attempt)
        assert isinstance(attempt_dict, dict)
        assert attempt_dict["attempt_id"] == "attempt_123"
        assert attempt_dict["method"] == VerificationMethod.EMAIL_VERIFICATION

    def test_verification_attempt_different_methods(self):
        """Test VerificationAttempt with different verification methods."""
        methods_to_test = [
            VerificationMethod.EMAIL_VERIFICATION,
            VerificationMethod.SMS_VERIFICATION,
            VerificationMethod.CREDIT_CARD_VERIFICATION,
            VerificationMethod.DIGITAL_SIGNATURE,
            VerificationMethod.VIDEO_CALL_VERIFICATION,
            VerificationMethod.GOVERNMENT_ID_VERIFICATION,
        ]

        for method in methods_to_test:
            attempt = VerificationAttempt(
                attempt_id=f"attempt_{method.value}",
                consent_id="test_consent",
                method=method,
                status=VerificationStatus.PENDING,
                attempted_at="2024-01-15T10:30:00",
            )

            assert attempt.method == method
            assert isinstance(attempt.method, VerificationMethod)

    def test_verification_attempt_status_lifecycle(self):
        """Test VerificationAttempt through different status states."""
        attempt = VerificationAttempt(
            attempt_id="lifecycle_test",
            consent_id="test_consent",
            method=VerificationMethod.EMAIL_VERIFICATION,
            status=VerificationStatus.PENDING,
            attempted_at="2024-01-15T10:30:00",
        )

        # Start as pending
        assert attempt.status == VerificationStatus.PENDING

        # Move to in progress
        attempt.status = VerificationStatus.IN_PROGRESS
        assert attempt.status == VerificationStatus.IN_PROGRESS

        # Complete successfully
        attempt.status = VerificationStatus.VERIFIED
        attempt.completed_at = "2024-01-15T10:35:00"
        assert attempt.status == VerificationStatus.VERIFIED
        assert attempt.completed_at is not None

    def test_verification_attempt_equality(self):
        """Test VerificationAttempt equality comparison."""
        attempt1 = VerificationAttempt(
            attempt_id="same_id",
            consent_id="consent1",
            method=VerificationMethod.EMAIL_VERIFICATION,
            status=VerificationStatus.PENDING,
            attempted_at="2024-01-15T10:30:00",
        )

        attempt2 = VerificationAttempt(
            attempt_id="same_id",
            consent_id="consent1",
            method=VerificationMethod.EMAIL_VERIFICATION,
            status=VerificationStatus.PENDING,
            attempted_at="2024-01-15T10:30:00",
        )

        attempt3 = VerificationAttempt(
            attempt_id="different_id",
            consent_id="consent1",
            method=VerificationMethod.EMAIL_VERIFICATION,
            status=VerificationStatus.PENDING,
            attempted_at="2024-01-15T10:30:00",
        )

        assert attempt1 == attempt2
        assert attempt1 != attempt3


class TestConsentModelsIntegration:
    """Test integration between consent models."""

    def test_models_work_together(self):
        """Test that consent models work together in realistic scenarios."""
        # Create a consent record
        consent = ConsentRecord(
            consent_id="integration_test_consent",
            parent_id="parent_integration",
            child_id="child_integration",
            feature="location_tracking",
            status="pending",
            requested_at="2024-01-15T10:30:00",
            expiry_date="2025-01-15T10:30:00",
        )

        # Create verification attempt for the consent
        verification = VerificationAttempt(
            attempt_id="integration_attempt",
            consent_id=consent.consent_id,
            method=VerificationMethod.EMAIL_VERIFICATION,
            status=VerificationStatus.PENDING,
            attempted_at="2024-01-15T10:35:00",
        )

        # Verify they're linked correctly
        assert verification.consent_id == consent.consent_id
        assert consent.status == "pending"
        assert verification.status == VerificationStatus.PENDING

        # Simulate successful verification
        verification.status = VerificationStatus.VERIFIED
        verification.completed_at = "2024-01-15T10:40:00"

        # Update consent accordingly
        consent.status = "granted"
        consent.granted_at = "2024-01-15T10:40:00"
        consent.verification_method = verification.method.value

        # Verify final state
        assert consent.status == "granted"
        assert consent.verification_method == "email_verification"
        assert verification.status == VerificationStatus.VERIFIED

    def test_coppa_compliance_data_model(self):
        """Test that data models support COPPA compliance requirements."""
        # COPPA requires detailed consent tracking
        consent = ConsentRecord(
            consent_id="coppa_compliance_test",
            parent_id="verified_parent_123",
            child_id="child_under_13",
            feature="personal_data_collection",
            status="granted",
            requested_at="2024-01-15T10:30:00",
            expiry_date="2025-01-15T10:30:00",
            granted_at="2024-01-15T11:00:00",
            verification_method="government_id_verification",
            metadata={
                "coppa_compliance": True,
                "child_age": 8,
                "verification_documents": ["government_id"],
                "audit_trail": ["requested", "parent_verified", "granted"],
            },
        )

        verification = VerificationAttempt(
            attempt_id="coppa_verification",
            consent_id=consent.consent_id,
            method=VerificationMethod.GOVERNMENT_ID_VERIFICATION,
            status=VerificationStatus.VERIFIED,
            attempted_at="2024-01-15T10:45:00",
            completed_at="2024-01-15T11:00:00",
        )

        # Verify COPPA requirements are met
        assert consent.parent_id is not None
        assert consent.child_id is not None
        assert consent.verification_method is not None
        assert consent.granted_at is not None
        assert consent.metadata["coppa_compliance"] is True
        assert verification.status == VerificationStatus.VERIFIED
