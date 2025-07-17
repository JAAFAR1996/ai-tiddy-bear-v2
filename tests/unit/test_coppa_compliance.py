"""
Comprehensive Unit Tests for COPPA Compliance Service
"""

import pytest
from datetime import datetime, timedelta
from unittest.mock import AsyncMock, MagicMock, patch
from uuid import uuid4

from src.infrastructure.security.hardening.coppa_compliance import (
    ProductionCOPPACompliance,
    ChildData,
    ConsentRecord,
    DataDeletionRequest,
)


@pytest.fixture
def coppa_service():
    """Create COPPA compliance service instance."""
    return ProductionCOPPACompliance(encryption_key=None)


@pytest.fixture
def mock_database():
    """Create mock database."""
    db = AsyncMock()
    return db


@pytest.fixture
def valid_consent_data():
    """Create valid consent data."""
    return {
        "parent_id": str(uuid4()),
        "parent_name": "John Doe",
        "parent_email": "parent@example.com",
        "child_name": "Alice",
        "child_age": 8,
        "data_collection_consent": True,
        "safety_monitoring_consent": True,
    }


@pytest.fixture
def child_data():
    """Create sample child data."""
    return ChildData(
        child_id=str(uuid4()),
        parent_id=str(uuid4()),
        age=7,
        parent_consent=True,
        encrypted_name=None,
        preferences_encrypted=None,
    )


class TestAgeValidation:
    """Test age validation for COPPA compliance."""

    @pytest.mark.asyncio
    async def test_validate_age_compliant(self, coppa_service):
        """Test age validation with compliant age."""
        result = await coppa_service.validate_child_age(8)

        assert result["compliant"] is True
        assert result["severity"] == "none"
        assert "within COPPA compliant range" in result["reason"]
        assert result["legal_risk"] == "none"

    @pytest.mark.asyncio
    async def test_validate_age_too_old(self, coppa_service):
        """Test age validation with age exceeding COPPA limit."""
        result = await coppa_service.validate_child_age(14)

        assert result["compliant"] is False
        assert result["severity"] == "high"
        assert "exceeds COPPA limit" in result["reason"]
        assert result["legal_risk"] == "high"
        assert result["required_action"] == "Service not available - COPPA violation"

    @pytest.mark.asyncio
    async def test_validate_age_too_young(self, coppa_service):
        """Test age validation with age below minimum (e.g., 2)."""
        result = await coppa_service.validate_child_age(2)

        assert result["compliant"] is False
        assert result["severity"] == "medium"
        assert "below minimum safe interaction age" in result["reason"]
        assert result["legal_risk"] == "medium"
        assert "Enhanced parental supervision" in result["required_action"]

    @pytest.mark.asyncio
    async def test_validate_age_zero(self, coppa_service):
        """Test age validation with age zero."""
        result = await coppa_service.validate_child_age(0)

        assert result["compliant"] is False
        assert result["severity"] == "high"
        assert "invalid age" in result["reason"]
        assert result["legal_risk"] == "high"
        assert result["required_action"] == "Service not available - Invalid age"

    @pytest.mark.asyncio
    async def test_validate_age_boundary_min(self, coppa_service):
        """Test age validation at minimum boundary (e.g., 3)."""
        result = await coppa_service.validate_child_age(3)

        assert result["compliant"] is True
        assert result["severity"] == "none"

    @pytest.mark.asyncio
    async def test_validate_age_boundary_max(self, coppa_service):
        """Test age validation at maximum boundary (e.g., 12 for COPPA compliance)."""
        result = await coppa_service.validate_child_age(12)

        assert result["compliant"] is True
        assert result["severity"] == "none"

    @pytest.mark.asyncio
    async def test_validate_age_exactly_coppa_limit(self, coppa_service):
        """Test age validation for exactly the COPPA limit (13), which should be non-compliant."""
        result = await coppa_service.validate_child_age(13)

        assert result["compliant"] is False
        assert result["severity"] == "high"
        assert "exceeds COPPA limit" in result["reason"]
        assert result["legal_risk"] == "high"
        assert result["required_action"] == "Service not available - COPPA violation"


class TestParentalConsent:
    """Test parental consent validation."""

    @pytest.mark.asyncio
    async def test_validate_consent_valid(
            self, coppa_service, valid_consent_data):
        """Test validation with valid consent data."""
        result = await coppa_service.validate_parental_consent(valid_consent_data)

        assert result["valid"] is True
        assert len(result["missing_fields"]) == 0
        assert len(result["invalid_fields"]) == 0
        assert result["compliance_score"] == 100

    @pytest.mark.asyncio
    async def test_validate_consent_missing_fields(self, coppa_service):
        """Test validation with missing required fields."""
        incomplete_data = {"parent_name": "John Doe", "child_age": 8}

        result = await coppa_service.validate_parental_consent(incomplete_data)

        assert result["valid"] is False
        assert "parent_email" in result["missing_fields"]
        assert "child_name" in result["missing_fields"]
        assert "data_collection_consent" in result["missing_fields"]
        assert result["compliance_score"] < 100

    @pytest.mark.asyncio
    async def test_validate_consent_invalid_email(
        self, coppa_service, valid_consent_data
    ):
        """Test validation with invalid email format."""
        valid_consent_data["parent_email"] = "not-an-email"

        result = await coppa_service.validate_parental_consent(valid_consent_data)

        assert result["valid"] is False
        assert "parent_email" in result["invalid_fields"]

    @pytest.mark.asyncio
    async def test_validate_consent_denied(
            self, coppa_service, valid_consent_data):
        """Test validation when consent is denied."""
        valid_consent_data["data_collection_consent"] = False

        result = await coppa_service.validate_parental_consent(valid_consent_data)

        assert result["valid"] is False
        assert "Missing data_collection_consent" in result["security_flags"]


class TestDataEncryption:
    """Test child data encryption."""

    @pytest.mark.asyncio
    async def test_encrypt_child_data(self, coppa_service):
        """Test data encryption."""
        original_data = "Alice's Secret Data"

        encrypted = await coppa_service.encrypt_child_data(original_data)

        assert encrypted != original_data
        assert isinstance(encrypted, str)
        assert len(encrypted) > len(original_data)

    @pytest.mark.asyncio
    async def test_decrypt_child_data(self, coppa_service):
        """Test data decryption."""
        original_data = "Alice's Secret Data"

        encrypted = await coppa_service.encrypt_child_data(original_data)
        decrypted = await coppa_service.decrypt_child_data(encrypted)

        assert decrypted == original_data

    @pytest.mark.asyncio
    async def test_encrypt_decrypt_unicode(self, coppa_service):
        """Test encryption/decryption with unicode data."""
        original_data = "Alice's Data with émojis 🧸"

        encrypted = await coppa_service.encrypt_child_data(original_data)
        decrypted = await coppa_service.decrypt_child_data(encrypted)

        assert decrypted == original_data

    @pytest.mark.asyncio
    async def test_decrypt_invalid_data(self, coppa_service):
        """Test decryption with invalid encrypted data."""
        with pytest.raises(ValueError, match="Failed to decrypt"):
            await coppa_service.decrypt_child_data("invalid_encrypted_data")


class TestConsentRecord:
    """Test consent record creation."""

    @pytest.mark.asyncio
    async def test_create_consent_record_success(
        self, coppa_service, valid_consent_data
    ):
        """Test successful consent record creation."""
        ip_address = "192.168.1.1"

        record = await coppa_service.create_consent_record(
            valid_consent_data, ip_address
        )

        assert isinstance(record, ConsentRecord)
        assert record.parent_email == valid_consent_data["parent_email"]
        assert record.parent_name == valid_consent_data["parent_name"]
        assert record.child_name == valid_consent_data["child_name"]
        assert record.child_age == valid_consent_data["child_age"]
        assert record.consent_ip_address == ip_address
        assert record.is_active is True
        assert len(record.data_types_consented) > 0

    @pytest.mark.asyncio
    async def test_create_consent_record_invalid_data(self, coppa_service):
        """Test consent record creation with invalid data."""
        invalid_data = {"parent_name": "John"}

        with pytest.raises(ValueError, match="Invalid consent data"):
            await coppa_service.create_consent_record(invalid_data)

    @pytest.mark.asyncio
    async def test_create_consent_record_with_database(
        self, coppa_service, valid_consent_data, mock_database
    ):
        """Test consent record creation with database storage."""
        coppa_service.database = mock_database
        coppa_service._store_consent_record = AsyncMock()

        record = await coppa_service.create_consent_record(valid_consent_data)

        assert record is not None
        coppa_service._store_consent_record.assert_called_once_with(record)


class TestDataDeletion:
    """Test data deletion scheduling."""

    @pytest.mark.asyncio
    async def test_schedule_data_deletion_default(self, coppa_service):
        """Test data deletion scheduling with default retention."""
        child_id = str(uuid4())

        policy = await coppa_service.schedule_data_deletion(child_id)

        assert policy["child_id"] == child_id
        assert policy["retention_period_days"] == 90
        assert policy["auto_deletion_enabled"] is True
        assert policy["parent_notification_required"] is True
        assert "conversation_history" in policy["data_types_to_delete"]
        assert "consent_records" in policy["data_types_to_retain"]

        # Check deletion date is 90 days from now
        deletion_date = datetime.fromisoformat(
            policy["scheduled_deletion_date"])
        expected_date = datetime.utcnow() + timedelta(days=90)
        assert abs((deletion_date - expected_date).total_seconds()) < 60

    @pytest.mark.asyncio
    async def test_schedule_data_deletion_custom_retention(
            self, coppa_service):
        """Test data deletion with custom retention period."""
        child_id = str(uuid4())
        retention_days = 30

        policy = await coppa_service.schedule_data_deletion(child_id, retention_days)

        assert policy["retention_period_days"] == retention_days

        # Check deletion date is 30 days from now
        deletion_date = datetime.fromisoformat(
            policy["scheduled_deletion_date"])
        expected_date = datetime.utcnow() + timedelta(days=retention_days)
        assert abs((deletion_date - expected_date).total_seconds()) < 60


class TestDataCollectionCompliance:
    """Test data collection compliance checking."""

    def test_check_data_collection_compliant(self, coppa_service):
        """Test compliant data collection."""
        data_to_collect = {
            "first_name": "Alice",
            "age": 8,
            "interests": ["reading", "games"],
            "language": "en",
        }

        result = coppa_service.check_data_collection_compliance(
            data_to_collect)

        assert result["compliant"] is True
        assert len(result["prohibited_data_found"]) == 0
        assert result["allowed_data"] == data_to_collect

    def test_check_data_collection_prohibited(self, coppa_service):
        """Test data collection with prohibited fields."""
        data_to_collect = {
            "first_name": "Alice",
            "last_name": "Smith",  # Prohibited
            "home_address": "123 Main St",  # Prohibited
            "age": 8,
        }

        result = coppa_service.check_data_collection_compliance(
            data_to_collect)

        assert result["compliant"] is False
        assert "last_name" in result["prohibited_data_found"]
        assert "home_address" in result["prohibited_data_found"]
        assert "first_name" in result["allowed_data"]
        assert "age" in result["allowed_data"]

    def test_check_data_collection_recommendations(self, coppa_service):
        """Test data collection recommendations."""
        data_to_collect = {
            "first_name": "Alice",
            "geolocation": "general_area",
            "photos": "avatar_only",
        }

        result = coppa_service.check_data_collection_compliance(
            data_to_collect)

        assert len(result["recommendations"]) > 0
        assert any(
            "general location" in rec for rec in result["recommendations"])
        assert any("photos" in rec for rec in result["recommendations"])


class TestPrivacyNotice:
    """Test privacy notice generation."""

    def test_generate_privacy_notice(self, coppa_service):
        """Test privacy notice generation."""
        child_age = 8

        notice = coppa_service.generate_privacy_notice(child_age)

        assert isinstance(notice, str)
        assert "Privacy Notice" in notice
        assert "AI Teddy Bear" in notice
        assert str(coppa_service.max_age) in notice
        assert "Information We Collect" in notice
        assert "How We Use Information" in notice
        assert "Data Protection" in notice
        assert "Your Rights" in notice
        assert "Contact Information" in notice
        assert datetime.now().strftime("%Y-%m-%d") in notice


class TestConsentForm:
    """Test consent form generation."""

    def test_create_consent_form(self, coppa_service):
        """Test consent form creation."""
        form = coppa_service.create_consent_form()

        assert "form_id" in form
        assert form["version"] == "1.0"
        assert len(form["required_fields"]) > 0

        # Check required fields
        field_names = [field["field"] for field in form["required_fields"]]
        assert "parent_name" in field_names
        assert "parent_email" in field_names
        assert "child_name" in field_names
        assert "child_age" in field_names
        assert "data_collection_consent" in field_names
        assert "safety_monitoring_consent" in field_names

        # Check legal text
        assert "legal_text" in form
        assert "parent or legal guardian" in form["legal_text"]

        # Check expiration
        assert "expiration_date" in form
        expiration = form["expiration_date"]
        assert expiration > datetime.now()


class TestAuditCompliance:
    """Test compliance audit functionality."""

    def test_audit_compliance(self, coppa_service):
        """Test compliance audit report generation."""
        report = coppa_service.audit_compliance()

        assert report["compliance_status"] == "compliant"
        assert len(report["checks_performed"]) > 0
        assert len(report["recommendations"]) > 0
        assert "next_audit_date" in report

        # Verify all required checks are present
        check_names = [check["check"] for check in report["checks_performed"]]
        assert "Age verification system" in check_names
        assert "Parental consent collection" in check_names
        assert "Data minimization" in check_names
        assert "Data retention policy" in check_names
        assert "Privacy notice" in check_names

        # Verify all checks passed
        for check in report["checks_performed"]:
            assert check["status"] == "passed"


class TestDataBreach:
    """Test data breach handling."""

    def test_handle_data_breach_low_severity(self, coppa_service):
        """Test handling low severity data breach."""
        breach_details = {
            "affected_count": 5,
            "exposed_data_types": ["preferences"]}

        response = coppa_service.handle_data_breach(breach_details)

        assert "breach_id" in response
        assert response["severity"] == "low"
        assert response["affected_children"] == 5
        assert response["notification_required"] is True
        assert len(response["immediate_actions"]) > 0
        assert "parent_notification_template" in response

    def test_handle_data_breach_high_severity(self, coppa_service):
        """Test handling high severity data breach."""
        breach_details = {
            "affected_count": 150,
            "exposed_data_types": ["personal_identifiers", "conversation_history"],
        }

        response = coppa_service.handle_data_breach(breach_details)

        assert response["severity"] == "high"
        assert response["affected_children"] == 150

        # Check regulatory deadline is 72 hours from now
        deadline = response["regulatory_report_deadline"]
        expected = datetime.now() + timedelta(hours=72)
        assert abs((deadline - expected).total_seconds()) < 60
