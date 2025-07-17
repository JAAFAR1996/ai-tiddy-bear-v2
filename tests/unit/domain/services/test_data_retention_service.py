"""
Tests for COPPA Data Retention Service
Testing centralized data retention policies for COPPA compliance.
"""

import pytest
from datetime import datetime, timedelta
from unittest.mock import Mock
from freezegun import freeze_time

from src.domain.services.data_retention_service import COPPADataRetentionService
from src.domain.models.data_retention_models import DataType, RetentionPolicy
from src.domain.services.coppa_age_validation import AgeValidationResult


class TestCOPPADataRetentionService:
    """Test the COPPA Data Retention Service."""

    @pytest.fixture
    def retention_service(self):
        """Create a retention service instance."""
        return COPPADataRetentionService()

    @pytest.fixture
    def mock_logger(self):
        """Create a mock logger."""
        return Mock()

    def test_initialization(self, retention_service):
        """Test service initialization."""
        assert retention_service._logger is not None
        assert retention_service.policies is not None
        assert isinstance(retention_service.policies, dict)
        assert "valid_child" in retention_service.policies
        assert "valid_teen" in retention_service.policies
        assert "valid_adult" in retention_service.policies

    def test_initialization_with_logger(self, mock_logger):
        """Test service initialization with custom logger."""
        service = COPPADataRetentionService(logger=mock_logger)
        assert service._logger == mock_logger

    # Test retention policy initialization
    def test_valid_child_policies(self, retention_service):
        """Test retention policies for valid children under 13."""
        child_policies = retention_service.policies["valid_child"]

        # Check conversation data policy
        conv_policy = child_policies[DataType.CONVERSATION_DATA]
        assert conv_policy.retention_days == 30
        assert conv_policy.auto_delete is True
        assert conv_policy.requires_consent is True

        # Check voice recordings policy
        voice_policy = child_policies[DataType.VOICE_RECORDINGS]
        assert voice_policy.retention_days == 7
        assert voice_policy.auto_delete is True
        assert voice_policy.requires_consent is True

        # Check consent records policy (longer retention)
        consent_policy = child_policies[DataType.CONSENT_RECORDS]
        assert consent_policy.retention_days == 2555  # 7 years
        assert consent_policy.auto_delete is False
        assert consent_policy.requires_consent is False

    def test_valid_teen_policies(self, retention_service):
        """Test retention policies for teenagers 13-17."""
        teen_policies = retention_service.policies["valid_teen"]

        # Check conversation data policy (longer than child)
        conv_policy = teen_policies[DataType.CONVERSATION_DATA]
        assert conv_policy.retention_days == 90
        assert conv_policy.auto_delete is True
        assert conv_policy.requires_consent is True

        # Check voice recordings policy
        voice_policy = teen_policies[DataType.VOICE_RECORDINGS]
        assert voice_policy.retention_days == 30
        assert voice_policy.auto_delete is True
        assert voice_policy.requires_consent is True

    def test_valid_adult_policies(self, retention_service):
        """Test retention policies for adults 18+."""
        adult_policies = retention_service.policies["valid_adult"]

        # Check conversation data policy (longest retention)
        conv_policy = adult_policies[DataType.CONVERSATION_DATA]
        assert conv_policy.retention_days == 365
        assert conv_policy.auto_delete is True
        assert conv_policy.requires_consent is False  # No parental consent needed

        # Check analytics data policy
        analytics_policy = adult_policies[DataType.ANALYTICS_DATA]
        assert analytics_policy.retention_days == 730  # 2 years
        assert analytics_policy.auto_delete is True
        assert analytics_policy.requires_consent is False

    # Test get_retention_policy
    def test_get_retention_policy_valid_child(self, retention_service):
        """Test getting retention policy for valid child."""
        policy = retention_service.get_retention_policy(
            8, DataType.CONVERSATION_DATA)

        assert policy is not None
        assert policy.retention_days == 30
        assert policy.auto_delete is True
        assert policy.requires_consent is True

    def test_get_retention_policy_valid_teen(self, retention_service):
        """Test getting retention policy for valid teen."""
        policy = retention_service.get_retention_policy(
            15, DataType.CONVERSATION_DATA)

        assert policy is not None
        assert policy.retention_days == 90
        assert policy.auto_delete is True
        assert policy.requires_consent is True

    def test_get_retention_policy_valid_adult(self, retention_service):
        """Test getting retention policy for valid adult."""
        policy = retention_service.get_retention_policy(
            25, DataType.CONVERSATION_DATA)

        assert policy is not None
        assert policy.retention_days == 365
        assert policy.auto_delete is True
        assert policy.requires_consent is False

    def test_get_retention_policy_invalid_age(self, retention_service):
        """Test getting retention policy for invalid age (uses most restrictive)."""
        policy = retention_service.get_retention_policy(
            -1, DataType.CONVERSATION_DATA)

        assert policy is not None
        # Should use child policy as most restrictive
        assert policy.retention_days == 30
        assert policy.auto_delete is True
        assert policy.requires_consent is True

    def test_get_retention_policy_all_data_types(self, retention_service):
        """Test getting retention policy for all data types."""
        age = 10  # Valid child

        for data_type in DataType:
            policy = retention_service.get_retention_policy(age, data_type)
            assert policy is not None
            assert isinstance(policy, RetentionPolicy)
            assert policy.data_type == data_type

    # Test calculate_deletion_date
    @freeze_time("2024-01-15 10:00:00")
    def test_calculate_deletion_date_valid_policy(self, retention_service):
        """Test calculating deletion date with valid policy."""
        created_at = datetime.utcnow()
        deletion_date = retention_service.calculate_deletion_date(
            10, DataType.CONVERSATION_DATA, created_at
        )

        expected_date = created_at + timedelta(days=30)
        assert deletion_date == expected_date

    @freeze_time("2024-01-15 10:00:00")
    def test_calculate_deletion_date_voice_recordings(self, retention_service):
        """Test calculating deletion date for voice recordings."""
        created_at = datetime.utcnow()
        deletion_date = retention_service.calculate_deletion_date(
            8, DataType.VOICE_RECORDINGS, created_at
        )

        expected_date = created_at + timedelta(days=7)
        assert deletion_date == expected_date

    @freeze_time("2024-01-15 10:00:00")
    def test_calculate_deletion_date_consent_records(self, retention_service):
        """Test calculating deletion date for consent records (7 years)."""
        created_at = datetime.utcnow()
        deletion_date = retention_service.calculate_deletion_date(
            10, DataType.CONSENT_RECORDS, created_at
        )

        expected_date = created_at + timedelta(days=2555)  # 7 years
        assert deletion_date == expected_date

    # Test should_delete_data
    @freeze_time("2024-01-15 10:00:00")
    def test_should_delete_data_not_expired(self, retention_service):
        """Test should_delete_data when data is not expired."""
        created_at = datetime.utcnow() - timedelta(days=15)

        # Child data has 30 day retention, so 15 days old should not be deleted
        should_delete = retention_service.should_delete_data(
            10, DataType.CONVERSATION_DATA, created_at
        )

        assert should_delete is False

    @freeze_time("2024-01-15 10:00:00")
    def test_should_delete_data_expired(self, retention_service):
        """Test should_delete_data when data is expired."""
        created_at = datetime.utcnow() - timedelta(days=35)

        # Child data has 30 day retention, so 35 days old should be deleted
        should_delete = retention_service.should_delete_data(
            10, DataType.CONVERSATION_DATA, created_at
        )

        assert should_delete is True

    @freeze_time("2024-01-15 10:00:00")
    def test_should_delete_data_exactly_expired(self, retention_service):
        """Test should_delete_data when data is exactly at expiration."""
        created_at = datetime.utcnow() - timedelta(days=30)

        # Child data has 30 day retention, so exactly 30 days old should be
        # deleted
        should_delete = retention_service.should_delete_data(
            10, DataType.CONVERSATION_DATA, created_at
        )

        assert should_delete is True

    # Test get_retention_summary
    def test_get_retention_summary_valid_child(self, retention_service):
        """Test getting retention summary for valid child."""
        summary = retention_service.get_retention_summary(10)

        assert summary["child_age"] == 10
        assert summary["age_group"] == "valid_child"
        assert summary["coppa_applicable"] is True
        assert "policies" in summary

        # Check specific policies
        conv_policy = summary["policies"]["conversation_data"]
        assert conv_policy["retention_days"] == 30
        assert conv_policy["auto_delete"] is True
        assert conv_policy["requires_consent"] is True
        assert conv_policy["retention_period_human"] == "1 month"

    def test_get_retention_summary_valid_teen(self, retention_service):
        """Test getting retention summary for valid teen."""
        summary = retention_service.get_retention_summary(15)

        assert summary["child_age"] == 15
        assert summary["age_group"] == "valid_teen"
        assert summary["coppa_applicable"] is False
        assert "policies" in summary

    def test_get_retention_summary_valid_adult(self, retention_service):
        """Test getting retention summary for valid adult."""
        summary = retention_service.get_retention_summary(25)

        assert summary["child_age"] == 25
        assert summary["age_group"] == "valid_adult"
        assert summary["coppa_applicable"] is False
        assert "policies" in summary

    def test_get_retention_summary_invalid_age(self, retention_service):
        """Test getting retention summary for invalid age."""
        summary = retention_service.get_retention_summary(-1)

        assert summary["child_age"] == -1
        assert summary["age_group"] == "valid_child"  # Most restrictive
        assert "policies" in summary

    # Test _format_retention_period
    def test_format_retention_period_days(self, retention_service):
        """Test formatting retention period in days."""
        assert retention_service._format_retention_period(7) == "7 days"
        assert retention_service._format_retention_period(15) == "15 days"
        assert retention_service._format_retention_period(29) == "29 days"

    def test_format_retention_period_months(self, retention_service):
        """Test formatting retention period in months."""
        assert retention_service._format_retention_period(30) == "1 month"
        assert retention_service._format_retention_period(60) == "2 months"
        assert retention_service._format_retention_period(90) == "3 months"
        assert retention_service._format_retention_period(180) == "6 months"

    def test_format_retention_period_years(self, retention_service):
        """Test formatting retention period in years."""
        assert retention_service._format_retention_period(365) == "1 year"
        assert retention_service._format_retention_period(730) == "2 years"
        assert retention_service._format_retention_period(1095) == "3 years"
        assert retention_service._format_retention_period(2555) == "7 years"

    # Test validate_retention_compliance
    def test_validate_retention_compliance_child_compliant(
            self, retention_service):
        """Test compliance validation for compliant child policies."""
        result = retention_service.validate_retention_compliance(10)

        assert result["compliant"] is True
        assert result["issues"] == []
        assert len(result["recommendations"]) > 0
        assert "retention_summary" in result

    def test_validate_retention_compliance_teen(self, retention_service):
        """Test compliance validation for teen (no COPPA)."""
        result = retention_service.validate_retention_compliance(15)

        assert result["compliant"] is True
        assert result["issues"] == []
        assert len(result["recommendations"]) == 0  # No COPPA recommendations

    def test_validate_retention_compliance_adult(self, retention_service):
        """Test compliance validation for adult."""
        result = retention_service.validate_retention_compliance(25)

        assert result["compliant"] is True
        assert result["issues"] == []
        assert len(result["recommendations"]) == 0

    # Test _get_compliance_recommendations
    def test_get_compliance_recommendations_coppa_child(
            self, retention_service):
        """Test compliance recommendations for COPPA-applicable child."""
        recommendations = retention_service._get_compliance_recommendations(10)

        assert len(recommendations) > 0
        assert any("automatic data deletion" in r for r in recommendations)
        assert any("parental consent" in r for r in recommendations)
        assert any("audit logs" in r for r in recommendations)

    def test_get_compliance_recommendations_teen(self, retention_service):
        """Test compliance recommendations for teen (no COPPA)."""
        recommendations = retention_service._get_compliance_recommendations(15)

        assert len(recommendations) == 0

    def test_get_compliance_recommendations_adult(self, retention_service):
        """Test compliance recommendations for adult."""
        recommendations = retention_service._get_compliance_recommendations(25)

        assert len(recommendations) == 0

    # Integration test
    def test_full_retention_workflow(self, retention_service):
        """Test complete retention workflow for a child."""
        child_age = 8
        data_type = DataType.VOICE_RECORDINGS
        created_at = datetime.utcnow() - timedelta(days=10)

        # Get policy
        policy = retention_service.get_retention_policy(child_age, data_type)
        assert policy.retention_days == 7

        # Calculate deletion date
        deletion_date = retention_service.calculate_deletion_date(
            child_age, data_type, created_at
        )
        assert deletion_date == created_at + timedelta(days=7)

        # Check if should delete
        should_delete = retention_service.should_delete_data(
            child_age, data_type, created_at
        )
        assert should_delete is True  # 10 days old > 7 day retention

        # Get summary
        summary = retention_service.get_retention_summary(child_age)
        assert summary["coppa_applicable"] is True

        # Validate compliance
        compliance = retention_service.validate_retention_compliance(child_age)
        assert compliance["compliant"] is True
