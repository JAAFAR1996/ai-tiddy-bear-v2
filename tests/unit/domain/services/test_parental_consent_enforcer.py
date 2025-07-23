"""Tests for Parental Consent Enforcement Service
Testing parental consent validation for child operations.
"""

from datetime import datetime, timedelta
from unittest.mock import Mock

import pytest

# Mock freezegun if not installed
try:
    from freezegun import freeze_time
except ImportError:
    # Create a simple mock that does nothing
    def freeze_time(time_to_freeze):
        def decorator(func):
            return func
        return decorator

from src.domain.models.consent_models_domain import (
    ConsentRecord,
    ConsentStatus,
    ConsentType,
)
from src.domain.services.coppa_age_validation import AgeValidationResult
from src.domain.services.parental_consent_enforcer import (
    ParentalConsentEnforcer,
)


class TestParentalConsentEnforcer:
    """Test the Parental Consent Enforcer service."""

    @pytest.fixture
    def consent_enforcer(self):
        """Create a consent enforcer instance."""
        return ParentalConsentEnforcer()

    @pytest.fixture
    def mock_logger(self):
        """Create a mock logger."""
        return Mock()

    @pytest.fixture
    def sample_consent_record(self):
        """Create a sample consent record."""
        return ConsentRecord(
            consent_id="consent_123",
            child_id="child_456",
            parent_id="parent_789",
            consent_type=ConsentType.DATA_COLLECTION,
            status=ConsentStatus.GRANTED,
            granted_at=datetime.utcnow(),
            expires_at=datetime.utcnow() + timedelta(days=365),
            verification_method="email_verification",
            granted_by="parent@example.com",
        )

    def test_initialization(self, consent_enforcer):
        """Test service initialization."""
        assert consent_enforcer._logger is not None
        assert consent_enforcer.required_consents is not None
        assert isinstance(consent_enforcer.consent_cache, dict)
        assert len(consent_enforcer.consent_cache) == 0

    def test_initialization_with_logger(self, mock_logger):
        """Test service initialization with custom logger."""
        enforcer = ParentalConsentEnforcer(logger=mock_logger)
        assert enforcer._logger == mock_logger

    # Test consent requirements initialization
    def test_required_consents_valid_child(self, consent_enforcer):
        """Test required consents for children under 13."""
        child_consents = consent_enforcer.required_consents["valid_child"]

        # All consent types should be required for children
        assert ConsentType.DATA_COLLECTION in child_consents
        assert ConsentType.VOICE_RECORDING in child_consents
        assert ConsentType.INTERACTION_LOGGING in child_consents
        assert ConsentType.ANALYTICS_COLLECTION in child_consents
        assert ConsentType.PROFILE_CREATION in child_consents
        assert ConsentType.AUDIO_PROCESSING in child_consents
        assert ConsentType.CONVERSATION_STORAGE in child_consents
        assert ConsentType.SAFETY_MONITORING in child_consents
        assert ConsentType.THIRD_PARTY_SHARING in child_consents
        assert ConsentType.MARKETING_COMMUNICATIONS in child_consents

        assert len(child_consents) == 10  # All consent types

    def test_required_consents_valid_teen(self, consent_enforcer):
        """Test required consents for teenagers 13-17."""
        teen_consents = consent_enforcer.required_consents["valid_teen"]

        # Limited consent types for teens
        assert ConsentType.DATA_COLLECTION in teen_consents
        assert ConsentType.VOICE_RECORDING in teen_consents
        assert ConsentType.PROFILE_CREATION in teen_consents
        assert ConsentType.THIRD_PARTY_SHARING in teen_consents
        assert ConsentType.MARKETING_COMMUNICATIONS in teen_consents

        assert len(teen_consents) == 5  # Fewer consent types

    def test_required_consents_valid_adult(self, consent_enforcer):
        """Test required consents for adults 18+."""
        adult_consents = consent_enforcer.required_consents["valid_adult"]

        # No parental consent required for adults
        assert len(adult_consents) == 0

    # Test get_required_consents
    def test_get_required_consents_child(self, consent_enforcer):
        """Test getting required consents for child."""
        consents = consent_enforcer.get_required_consents(8)

        assert len(consents) == 10
        assert ConsentType.DATA_COLLECTION in consents
        assert ConsentType.VOICE_RECORDING in consents

    def test_get_required_consents_teen(self, consent_enforcer):
        """Test getting required consents for teen."""
        consents = consent_enforcer.get_required_consents(15)

        assert len(consents) == 5
        assert ConsentType.DATA_COLLECTION in consents
        assert ConsentType.THIRD_PARTY_SHARING in consents

    def test_get_required_consents_adult(self, consent_enforcer):
        """Test getting required consents for adult."""
        consents = consent_enforcer.get_required_consents(25)

        assert len(consents) == 0

    def test_get_required_consents_invalid_age(self, consent_enforcer):
        """Test getting required consents for invalid age."""
        # Should use most restrictive (child) requirements
        consents = consent_enforcer.get_required_consents(-1)

        assert len(consents) == 10  # Child requirements

    # Test validate_consent_for_operation
    def test_validate_consent_adult_no_consent_required(self, consent_enforcer):
        """Test validation for adult where no consent is required."""
        result = consent_enforcer.validate_consent_for_operation(
            child_id="adult_123",
            child_age=25,
            operation_type=ConsentType.DATA_COLLECTION,
            consent_records=[],
        )

        assert result["consent_required"] is False
        assert result["consent_status"] == ConsentStatus.NOT_REQUIRED.value
        assert result["can_proceed"] is True
        assert "not required" in result["message"].lower()

    def test_validate_consent_child_missing_consent(self, consent_enforcer):
        """Test validation for child with missing consent."""
        result = consent_enforcer.validate_consent_for_operation(
            child_id="child_123",
            child_age=8,
            operation_type=ConsentType.DATA_COLLECTION,
            consent_records=[],  # No consent records
        )

        assert result["consent_required"] is True
        assert result["consent_status"] == ConsentStatus.PENDING.value
        assert result["can_proceed"] is False
        assert "required for" in result["message"].lower()
        assert result["required_action"] == "obtain_parental_consent"

    def test_validate_consent_child_valid_consent(
        self, consent_enforcer, sample_consent_record
    ):
        """Test validation for child with valid consent."""
        result = consent_enforcer.validate_consent_for_operation(
            child_id="child_456",
            child_age=8,
            operation_type=ConsentType.DATA_COLLECTION,
            consent_records=[sample_consent_record],
        )

        assert result["consent_required"] is True
        assert result["consent_status"] == ConsentStatus.GRANTED.value
        assert result["can_proceed"] is True
        assert "valid parental consent" in result["message"].lower()
        assert "consent_record" in result

    @freeze_time("2024-01-15")
    def test_validate_consent_expired(self, consent_enforcer):
        """Test validation with expired consent."""
        expired_consent = ConsentRecord(
            consent_id="consent_123",
            child_id="child_456",
            parent_id="parent_789",
            consent_type=ConsentType.DATA_COLLECTION,
            status=ConsentStatus.GRANTED,
            granted_at=datetime(2023, 1, 1),
            expires_at=datetime(2023, 12, 31),  # Expired
            verification_method="email_verification",
            granted_by="parent@example.com",
        )

        result = consent_enforcer.validate_consent_for_operation(
            child_id="child_456",
            child_age=8,
            operation_type=ConsentType.DATA_COLLECTION,
            consent_records=[expired_consent],
        )

        assert result["consent_required"] is True
        assert result["can_proceed"] is False
        assert result["required_action"] == "renew_parental_consent"

    def test_validate_consent_revoked(self, consent_enforcer):
        """Test validation with revoked consent."""
        revoked_consent = ConsentRecord(
            consent_id="consent_123",
            child_id="child_456",
            parent_id="parent_789",
            consent_type=ConsentType.DATA_COLLECTION,
            status=ConsentStatus.REVOKED,
            granted_at=datetime.utcnow(),
            expires_at=datetime.utcnow() + timedelta(days=365),
            verification_method="email_verification",
            granted_by="parent@example.com",
        )

        result = consent_enforcer.validate_consent_for_operation(
            child_id="child_456",
            child_age=8,
            operation_type=ConsentType.DATA_COLLECTION,
            consent_records=[revoked_consent],
        )

        assert result["consent_required"] is True
        assert result["can_proceed"] is False
        assert result["consent_status"] == ConsentStatus.REVOKED.value

    # Test validate_all_required_consents
    def test_validate_all_consents_adult(self, consent_enforcer):
        """Test validating all consents for adult."""
        result = consent_enforcer.validate_all_required_consents(
            child_id="adult_123", child_age=25, consent_records=[]
        )

        assert result["all_consents_valid"] is True
        assert result["missing_consents"] == []
        assert result["expired_consents"] == []
        assert result["valid_consents"] == []
        assert result["can_interact"] is True
        assert "no parental consent required" in result["message"].lower()

    def test_validate_all_consents_child_all_valid(self, consent_enforcer):
        """Test validating all consents for child with all valid consents."""
        # Create consent records for all required types
        consent_records = []
        for consent_type in consent_enforcer.get_required_consents(8):
            consent = ConsentRecord(
                consent_id=f"consent_{consent_type.value}",
                child_id="child_123",
                parent_id="parent_456",
                consent_type=consent_type,
                status=ConsentStatus.GRANTED,
                granted_at=datetime.utcnow(),
                expires_at=datetime.utcnow() + timedelta(days=365),
                verification_method="email_verification",
                granted_by="parent@example.com",
            )
            consent_records.append(consent)

        result = consent_enforcer.validate_all_required_consents(
            child_id="child_123", child_age=8, consent_records=consent_records
        )

        assert result["all_consents_valid"] is True
        assert result["missing_consents"] == []
        assert result["expired_consents"] == []
        assert len(result["valid_consents"]) == 10
        assert result["can_interact"] is True
        assert result["coppa_applicable"] is True

    def test_validate_all_consents_child_some_missing(self, consent_enforcer):
        """Test validating all consents with some missing."""
        # Only provide consent for data collection
        consent_records = [
            ConsentRecord(
                consent_id="consent_123",
                child_id="child_456",
                parent_id="parent_789",
                consent_type=ConsentType.DATA_COLLECTION,
                status=ConsentStatus.GRANTED,
                granted_at=datetime.utcnow(),
                expires_at=datetime.utcnow() + timedelta(days=365),
                verification_method="email_verification",
                granted_by="parent@example.com",
            )
        ]

        result = consent_enforcer.validate_all_required_consents(
            child_id="child_456", child_age=8, consent_records=consent_records
        )

        assert result["all_consents_valid"] is False
        assert len(result["missing_consents"]) == 9  # Missing 9 consent types
        assert len(result["valid_consents"]) == 1
        assert result["can_interact"] is False
        assert "Missing consent for" in result["message"]

    # Test helper methods
    def test_find_consent_record(self, consent_enforcer, sample_consent_record):
        """Test finding consent record by type."""
        consent_records = [sample_consent_record]

        # Find existing consent
        found = consent_enforcer._find_consent_record(
            consent_records, ConsentType.DATA_COLLECTION
        )
        assert found == sample_consent_record

        # Try to find non-existing consent
        not_found = consent_enforcer._find_consent_record(
            consent_records, ConsentType.VOICE_RECORDING
        )
        assert not_found is None

    def test_is_consent_valid(self, consent_enforcer):
        """Test consent validity checking."""
        # Valid consent
        valid_consent = ConsentRecord(
            consent_id="consent_123",
            child_id="child_456",
            parent_id="parent_789",
            consent_type=ConsentType.DATA_COLLECTION,
            status=ConsentStatus.GRANTED,
            granted_at=datetime.utcnow(),
            expires_at=datetime.utcnow() + timedelta(days=365),
            verification_method="email_verification",
            granted_by="parent@example.com",
        )
        assert consent_enforcer._is_consent_valid(valid_consent) is True

        # Revoked consent
        revoked_consent = ConsentRecord(
            consent_id="consent_123",
            child_id="child_456",
            parent_id="parent_789",
            consent_type=ConsentType.DATA_COLLECTION,
            status=ConsentStatus.REVOKED,
            granted_at=datetime.utcnow(),
            expires_at=datetime.utcnow() + timedelta(days=365),
            verification_method="email_verification",
            granted_by="parent@example.com",
        )
        assert consent_enforcer._is_consent_valid(revoked_consent) is False

        # Expired consent
        expired_consent = ConsentRecord(
            consent_id="consent_123",
            child_id="child_456",
            parent_id="parent_789",
            consent_type=ConsentType.DATA_COLLECTION,
            status=ConsentStatus.GRANTED,
            granted_at=datetime.utcnow() - timedelta(days=400),
            expires_at=datetime.utcnow() - timedelta(days=35),
            verification_method="email_verification",
            granted_by="parent@example.com",
        )
        assert consent_enforcer._is_consent_valid(expired_consent) is False

    def test_consent_record_to_dict(self, consent_enforcer, sample_consent_record):
        """Test converting consent record to dictionary."""
        result = consent_enforcer._consent_record_to_dict(sample_consent_record)

        assert result["consent_id"] == "consent_123"
        assert result["consent_type"] == ConsentType.DATA_COLLECTION.value
        assert result["status"] == ConsentStatus.GRANTED.value
        assert result["verification_method"] == "email_verification"
        assert "granted_at" in result
        assert "expires_at" in result

    def test_generate_consent_message(self, consent_enforcer):
        """Test generating consent status messages."""
        # All valid
        msg = consent_enforcer._generate_consent_message(True, [], [])
        assert "all required parental consents are valid" in msg.lower()

        # Missing consents
        msg = consent_enforcer._generate_consent_message(
            False, ["data_collection", "voice_recording"], []
        )
        assert "missing consent for" in msg.lower()
        assert "data_collection" in msg
        assert "voice_recording" in msg

        # Expired consents
        msg = consent_enforcer._generate_consent_message(
            False, [], ["profile_creation", "analytics_collection"]
        )
        assert "expired consent for" in msg.lower()
        assert "profile_creation" in msg
        assert "analytics_collection" in msg

        # Both missing and expired
        msg = consent_enforcer._generate_consent_message(
            False, ["data_collection"], ["voice_recording"]
        )
        assert "missing consent" in msg.lower()
        assert "expired consent" in msg.lower()

    # Test get_consent_requirements_summary
    def test_get_consent_requirements_summary_child(self, consent_enforcer):
        """Test getting consent requirements summary for child."""
        summary = consent_enforcer.get_consent_requirements_summary(8)

        assert summary["child_age"] == 8
        assert summary["age_validation"] == AgeValidationResult.VALID_CHILD.value
        assert summary["coppa_applicable"] is True
        assert summary["consent_required"] is True
        assert summary["total_required_consents"] == 10
        assert summary["compliance_level"] == "strict_coppa_compliance"
        assert len(summary["recommendations"]) > 0

    def test_get_consent_requirements_summary_teen(self, consent_enforcer):
        """Test getting consent requirements summary for teen."""
        summary = consent_enforcer.get_consent_requirements_summary(15)

        assert summary["child_age"] == 15
        assert summary["age_validation"] == AgeValidationResult.VALID_TEEN.value
        assert summary["coppa_applicable"] is False
        assert summary["consent_required"] is True
        assert summary["total_required_consents"] == 5
        assert summary["compliance_level"] == "moderate_parental_oversight"
        assert len(summary["recommendations"]) > 0

    def test_get_consent_requirements_summary_adult(self, consent_enforcer):
        """Test getting consent requirements summary for adult."""
        summary = consent_enforcer.get_consent_requirements_summary(25)

        assert summary["child_age"] == 25
        assert summary["age_validation"] == AgeValidationResult.VALID_ADULT.value
        assert summary["coppa_applicable"] is False
        assert summary["consent_required"] is False
        assert summary["total_required_consents"] == 0
        assert summary["compliance_level"] == "standard_privacy_protection"
        assert len(summary["recommendations"]) == 0

    # Test compliance level and recommendations
    def test_get_compliance_level(self, consent_enforcer):
        """Test getting compliance level for different age validations."""
        assert (
            consent_enforcer._get_compliance_level(AgeValidationResult.VALID_CHILD)
            == "strict_coppa_compliance"
        )

        assert (
            consent_enforcer._get_compliance_level(AgeValidationResult.VALID_TEEN)
            == "moderate_parental_oversight"
        )

        assert (
            consent_enforcer._get_compliance_level(AgeValidationResult.VALID_ADULT)
            == "standard_privacy_protection"
        )

        assert (
            consent_enforcer._get_compliance_level(AgeValidationResult.TOO_YOUNG)
            == "blocked_interaction"
        )

    def test_get_consent_recommendations_child(self, consent_enforcer):
        """Test getting consent recommendations for COPPA child."""
        recommendations = consent_enforcer._get_consent_recommendations(8)

        assert len(recommendations) == 5
        assert any("verifiable parental consent" in r for r in recommendations)
        assert any("consent expiration" in r for r in recommendations)
        assert any("consent withdrawal" in r for r in recommendations)
        assert any("audit logs" in r for r in recommendations)
        assert any("secure verification" in r for r in recommendations)

    def test_get_consent_recommendations_teen(self, consent_enforcer):
        """Test getting consent recommendations for teen."""
        recommendations = consent_enforcer._get_consent_recommendations(15)

        assert len(recommendations) == 3
        assert any("parental consent" in r for r in recommendations)
        assert any("privacy-by-design" in r for r in recommendations)
        assert any("parental visibility" in r for r in recommendations)

    def test_get_consent_recommendations_adult(self, consent_enforcer):
        """Test getting consent recommendations for adult."""
        recommendations = consent_enforcer._get_consent_recommendations(25)

        assert len(recommendations) == 0
