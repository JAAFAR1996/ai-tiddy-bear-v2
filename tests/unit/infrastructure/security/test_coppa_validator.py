"""
Tests for COPPA Validator
Testing COPPA age validation, compliance levels, and child safety requirements.
"""

import pytest
from unittest.mock import patch

from src.infrastructure.security.coppa_validator import (
    COPPAValidator,
    COPPAComplianceLevel,
    COPPAValidationResult,
    coppa_validator,
    is_coppa_subject,
    requires_parental_consent,
    get_data_retention_days,
    validate_child_age,
)


class TestCOPPAComplianceLevel:
    """Test the COPPAComplianceLevel enum."""

    def test_coppa_compliance_levels(self):
        """Test COPPA compliance level enumeration."""
        assert COPPAComplianceLevel.UNDER_COPPA.value == "under_coppa"
        assert (
            COPPAComplianceLevel.COPPA_TRANSITION.value == "coppa_transition"
        )
        assert (
            COPPAComplianceLevel.GENERAL_PROTECTION.value
            == "general_protection"
        )

    def test_coppa_compliance_level_coverage(self):
        """Test all COPPA compliance levels are defined."""
        levels = [level.value for level in COPPAComplianceLevel]
        expected_levels = [
            "under_coppa",
            "coppa_transition",
            "general_protection",
        ]
        assert sorted(levels) == sorted(expected_levels)


class TestCOPPAValidationResult:
    """Test the COPPAValidationResult dataclass."""

    def test_coppa_validation_result_creation(self):
        """Test COPPAValidationResult creation with all fields."""
        special_protections = {
            "enhanced_content_filtering": True,
            "restricted_data_sharing": True,
            "parental_oversight_required": True,
            "anonymized_analytics_only": True,
            "encrypted_storage_required": True,
            "audit_trail_required": True,
        }

        result = COPPAValidationResult(
            is_coppa_subject=True,
            compliance_level=COPPAComplianceLevel.UNDER_COPPA,
            parental_consent_required=True,
            data_retention_days=90,
            special_protections=special_protections,
            age_verified=True,
        )

        assert result.is_coppa_subject is True
        assert result.compliance_level == COPPAComplianceLevel.UNDER_COPPA
        assert result.parental_consent_required is True
        assert result.data_retention_days == 90
        assert result.special_protections == special_protections
        assert result.age_verified is True

    def test_coppa_validation_result_all_fields(self):
        """Test COPPAValidationResult has all required fields."""
        special_protections = {}
        result = COPPAValidationResult(
            is_coppa_subject=False,
            compliance_level=COPPAComplianceLevel.GENERAL_PROTECTION,
            parental_consent_required=False,
            data_retention_days=365,
            special_protections=special_protections,
            age_verified=True,
        )

        # Check all fields are accessible
        assert hasattr(result, "is_coppa_subject")
        assert hasattr(result, "compliance_level")
        assert hasattr(result, "parental_consent_required")
        assert hasattr(result, "data_retention_days")
        assert hasattr(result, "special_protections")
        assert hasattr(result, "age_verified")


class TestCOPPAValidator:
    """Test the COPPAValidator class."""

    @pytest.fixture
    def validator(self):
        """Create a COPPAValidator instance."""
        return COPPAValidator()

    @pytest.fixture
    def mock_coppa_enabled(self):
        """Mock COPPA enabled configuration."""
        with patch(
            "src.infrastructure.security.coppa_validator.is_coppa_enabled"
        ) as mock:
            mock.return_value = True
            yield mock

    @pytest.fixture
    def mock_coppa_disabled(self):
        """Mock COPPA disabled configuration."""
        with patch(
            "src.infrastructure.security.coppa_validator.is_coppa_enabled"
        ) as mock:
            mock.return_value = False
            yield mock

    def test_validator_initialization(self, validator):
        """Test COPPAValidator initialization."""
        assert validator.COPPA_AGE_LIMIT == 13
        assert validator.MIN_CHILD_AGE == 3
        assert validator.MAX_CHILD_AGE == 13
        assert validator.COPPA_RETENTION_DAYS == 90
        assert validator.TRANSITION_RETENTION_DAYS == 365
        assert hasattr(validator, "_validation_cache")

    def test_validator_constants(self, validator):
        """Test COPPA validator constants are correct."""
        assert validator.COPPA_AGE_LIMIT == 13
        assert validator.MIN_CHILD_AGE == 3
        assert validator.MAX_CHILD_AGE == 13
        assert validator.COPPA_RETENTION_DAYS == 90
        assert validator.TRANSITION_RETENTION_DAYS == 365

    @pytest.mark.parametrize(
        "age,expected_coppa_subject",
        [
            (3, True),
            (7, True),
            (12, True),
            (13, False),
            (15, False),
            (16, False),
        ],
    )
    def test_validate_age_compliance_coppa_enabled(
        self, validator, mock_coppa_enabled, age, expected_coppa_subject
    ):
        """Test age validation when COPPA is enabled."""
        result = validator.validate_age_compliance(age)

        assert result.is_coppa_subject == expected_coppa_subject
        assert result.age_verified is True
        assert result.special_protections["encrypted_storage_required"] is True
        assert result.special_protections["audit_trail_required"] is True

        if expected_coppa_subject:
            assert result.compliance_level == COPPAComplianceLevel.UNDER_COPPA
            assert result.parental_consent_required is True
            assert result.data_retention_days == 90
            assert (
                result.special_protections["enhanced_content_filtering"]
                is True
            )
            assert (
                result.special_protections["restricted_data_sharing"] is True
            )
            assert (
                result.special_protections["parental_oversight_required"]
                is True
            )
            assert (
                result.special_protections["anonymized_analytics_only"] is True
            )

    @pytest.mark.parametrize("age", [3, 7, 12, 13, 15, 16])
    def test_validate_age_compliance_coppa_disabled(
        self, validator, mock_coppa_disabled, age
    ):
        """Test age validation when COPPA is disabled."""
        result = validator.validate_age_compliance(age)

        assert result.is_coppa_subject is False
        assert (
            result.compliance_level == COPPAComplianceLevel.GENERAL_PROTECTION
        )
        assert result.parental_consent_required is False
        assert result.data_retention_days == 365 * 2
        assert result.age_verified is True

        # Still some protections enabled for safety
        assert result.special_protections["enhanced_content_filtering"] is True
        assert result.special_protections["encrypted_storage_required"] is True

        # COPPA-specific protections disabled
        assert result.special_protections["restricted_data_sharing"] is False
        assert (
            result.special_protections["parental_oversight_required"] is False
        )
        assert result.special_protections["anonymized_analytics_only"] is False
        assert result.special_protections["audit_trail_required"] is False

    def test_validate_age_compliance_transition_age(
        self, validator, mock_coppa_enabled
    ):
        """Test age validation for transition age (13-15)."""
        result = validator.validate_age_compliance(14)

        assert result.is_coppa_subject is False
        assert result.compliance_level == COPPAComplianceLevel.COPPA_TRANSITION
        assert result.parental_consent_required is False
        assert result.data_retention_days == 365
        assert result.special_protections["enhanced_content_filtering"] is True
        assert result.special_protections["restricted_data_sharing"] is False

    def test_validate_age_compliance_general_protection(
        self, validator, mock_coppa_enabled
    ):
        """Test age validation for general protection age (16+)."""
        result = validator.validate_age_compliance(16)

        assert result.is_coppa_subject is False
        assert (
            result.compliance_level == COPPAComplianceLevel.GENERAL_PROTECTION
        )
        assert result.parental_consent_required is False
        assert result.data_retention_days == 365
        assert (
            result.special_protections["enhanced_content_filtering"] is False
        )
        assert result.special_protections["restricted_data_sharing"] is False

    @pytest.mark.parametrize(
        "invalid_age",
        [
            "12",  # String instead of int
            12.5,  # Float instead of int
            None,  # None value
            [12],  # List
            {"age": 12},  # Dict
        ],
    )
    def test_validate_age_compliance_invalid_type(
        self, validator, mock_coppa_enabled, invalid_age
    ):
        """Test age validation with invalid data types."""
        with pytest.raises(ValueError, match="Age must be an integer"):
            validator.validate_age_compliance(invalid_age)

    @pytest.mark.parametrize("invalid_age", [2, 0, -1, -5])
    def test_validate_age_compliance_too_young(
        self, validator, mock_coppa_enabled, invalid_age
    ):
        """Test age validation for ages too young."""
        with pytest.raises(ValueError, match="is below minimum allowed age"):
            validator.validate_age_compliance(invalid_age)

    def test_validate_age_compliance_too_old_strict(
        self, validator, mock_coppa_enabled
    ):
        """Test age validation for ages too old with strict validation."""
        with pytest.raises(ValueError, match="exceeds maximum child age"):
            validator.validate_age_compliance(17, strict_validation=True)

    def test_validate_age_compliance_too_old_not_strict(
        self, validator, mock_coppa_enabled
    ):
        """Test age validation for ages too old without strict validation."""
        # Should not raise exception when strict_validation=False
        result = validator.validate_age_compliance(17, strict_validation=False)
        assert (
            result.compliance_level == COPPAComplianceLevel.GENERAL_PROTECTION
        )

    def test_validate_age_compliance_coppa_disabled_age_limits(
        self, validator, mock_coppa_disabled
    ):
        """Test age validation with COPPA disabled still validates basic limits."""
        with pytest.raises(ValueError, match="is outside acceptable range"):
            validator.validate_age_compliance(25)

        with pytest.raises(ValueError, match="is outside acceptable range"):
            validator.validate_age_compliance(0)

    @pytest.mark.parametrize(
        "age,expected",
        [
            (3, True),
            (7, True),
            (12, True),
            (13, False),
            (15, False),
            (16, False),
        ],
    )
    def test_is_coppa_subject_enabled(
        self, validator, mock_coppa_enabled, age, expected
    ):
        """Test is_coppa_subject method when COPPA is enabled."""
        result = validator.is_coppa_subject(age)
        assert result == expected

    @pytest.mark.parametrize("age", [3, 7, 12, 13, 15, 16])
    def test_is_coppa_subject_disabled(
        self, validator, mock_coppa_disabled, age
    ):
        """Test is_coppa_subject method when COPPA is disabled."""
        result = validator.is_coppa_subject(age)
        assert result is False

    def test_is_coppa_subject_invalid_age(self, validator, mock_coppa_enabled):
        """Test is_coppa_subject with invalid age defaults to True."""
        result = validator.is_coppa_subject(-1)
        assert result is True

    @pytest.mark.parametrize(
        "age,expected_days",
        [
            (3, 90),
            (7, 90),
            (12, 90),
            (13, 365),
            (14, 365),
            (15, 365),
            (16, 365),
        ],
    )
    def test_get_data_retention_period_enabled(
        self, validator, mock_coppa_enabled, age, expected_days
    ):
        """Test data retention period calculation when COPPA is enabled."""
        result = validator.get_data_retention_period(age)
        assert result == expected_days

    @pytest.mark.parametrize("age", [3, 7, 12, 13, 15, 16])
    def test_get_data_retention_period_disabled(
        self, validator, mock_coppa_disabled, age
    ):
        """Test data retention period when COPPA is disabled."""
        result = validator.get_data_retention_period(age)
        assert result == 365 * 2  # 2 years when COPPA disabled

    def test_get_data_retention_period_invalid_age(
        self, validator, mock_coppa_enabled
    ):
        """Test data retention period with invalid age uses COPPA retention."""
        result = validator.get_data_retention_period(-1)
        assert result == 90  # COPPA_RETENTION_DAYS

    @pytest.mark.parametrize(
        "age,expected",
        [
            (3, True),
            (7, True),
            (12, True),
            (13, False),
            (15, False),
            (16, False),
        ],
    )
    def test_requires_parental_consent_enabled(
        self, validator, mock_coppa_enabled, age, expected
    ):
        """Test parental consent requirement when COPPA is enabled."""
        result = validator.requires_parental_consent(age)
        assert result == expected

    @pytest.mark.parametrize("age", [3, 7, 12, 13, 15, 16])
    def test_requires_parental_consent_disabled(
        self, validator, mock_coppa_disabled, age
    ):
        """Test parental consent requirement when COPPA is disabled."""
        result = validator.requires_parental_consent(age)
        assert result is False

    @pytest.mark.parametrize(
        "age,expected_level",
        [
            (3, "strict"),
            (7, "strict"),
            (12, "strict"),
            (13, "moderate"),
            (14, "moderate"),
            (15, "moderate"),
            (16, "standard"),
        ],
    )
    def test_get_content_filtering_level_enabled(
        self, validator, mock_coppa_enabled, age, expected_level
    ):
        """Test content filtering level determination when COPPA is enabled."""
        result = validator.get_content_filtering_level(age)
        assert result == expected_level

    @pytest.mark.parametrize("age", [3, 7, 12, 13, 15, 16])
    def test_get_content_filtering_level_disabled(
        self, validator, mock_coppa_disabled, age
    ):
        """Test content filtering level when COPPA is disabled."""
        result = validator.get_content_filtering_level(age)
        assert result == "standard"  # General protection level

    def test_get_content_filtering_level_invalid_age(
        self, validator, mock_coppa_enabled
    ):
        """Test content filtering level with invalid age uses strictest."""
        result = validator.get_content_filtering_level(-1)
        assert result == "strict"

    @pytest.mark.parametrize(
        "age,min_age,max_age,expected",
        [
            (5, 3, 13, True),
            (3, 3, 13, True),
            (13, 3, 13, True),
            (2, 3, 13, False),
            (14, 3, 13, False),
            (10, 5, 12, True),
            (4, 5, 12, False),
            (13, 5, 12, False),
        ],
    )
    def test_validate_age_range_with_params(
        self, validator, mock_coppa_enabled, age, min_age, max_age, expected
    ):
        """Test age range validation with custom parameters."""
        result = validator.validate_age_range(age, min_age, max_age)
        assert result == expected

    def test_validate_age_range_default_params(
        self, validator, mock_coppa_enabled
    ):
        """Test age range validation with default parameters."""
        assert validator.validate_age_range(5) is True
        assert validator.validate_age_range(2) is False
        assert validator.validate_age_range(14) is False

    def test_validate_age_range_invalid_type(
        self, validator, mock_coppa_enabled
    ):
        """Test age range validation with invalid data type."""
        assert validator.validate_age_range("5") is False
        assert validator.validate_age_range(5.5) is False
        assert validator.validate_age_range(None) is False

    def test_validate_age_range_validation_exception(
        self, validator, mock_coppa_enabled
    ):
        """Test age range validation handles validation exceptions."""
        with patch.object(
            validator,
            "validate_age_compliance",
            side_effect=ValueError("Test error"),
        ):
            result = validator.validate_age_range(5)
            assert result is False


class TestCOPPAValidatorGlobalFunctions:
    """Test global COPPA validator functions."""

    @pytest.fixture
    def mock_coppa_enabled(self):
        """Mock COPPA enabled configuration."""
        with patch(
            "src.infrastructure.security.coppa_validator.is_coppa_enabled"
        ) as mock:
            mock.return_value = True
            yield mock

    @pytest.fixture
    def mock_coppa_disabled(self):
        """Mock COPPA disabled configuration."""
        with patch(
            "src.infrastructure.security.coppa_validator.is_coppa_enabled"
        ) as mock:
            mock.return_value = False
            yield mock

    @pytest.mark.parametrize(
        "age,expected",
        [
            (3, True),
            (7, True),
            (12, True),
            (13, False),
            (15, False),
            (16, False),
        ],
    )
    def test_is_coppa_subject_function_enabled(
        self, mock_coppa_enabled, age, expected
    ):
        """Test global is_coppa_subject function when COPPA is enabled."""
        result = is_coppa_subject(age)
        assert result == expected

    @pytest.mark.parametrize("age", [3, 7, 12, 13, 15, 16])
    def test_is_coppa_subject_function_disabled(
        self, mock_coppa_disabled, age
    ):
        """Test global is_coppa_subject function when COPPA is disabled."""
        result = is_coppa_subject(age)
        assert result is False

    @pytest.mark.parametrize(
        "age,expected",
        [
            (3, True),
            (7, True),
            (12, True),
            (13, False),
            (15, False),
            (16, False),
        ],
    )
    def test_requires_parental_consent_function_enabled(
        self, mock_coppa_enabled, age, expected
    ):
        """Test global requires_parental_consent function when COPPA is enabled."""
        result = requires_parental_consent(age)
        assert result == expected

    @pytest.mark.parametrize("age", [3, 7, 12, 13, 15, 16])
    def test_requires_parental_consent_function_disabled(
        self, mock_coppa_disabled, age
    ):
        """Test global requires_parental_consent function when COPPA is disabled."""
        result = requires_parental_consent(age)
        assert result is False

    @pytest.mark.parametrize(
        "age,expected_days",
        [
            (3, 90),
            (7, 90),
            (12, 90),
            (13, 365),
            (14, 365),
            (15, 365),
            (16, 365),
        ],
    )
    def test_get_data_retention_days_function_enabled(
        self, mock_coppa_enabled, age, expected_days
    ):
        """Test global get_data_retention_days function when COPPA is enabled."""
        result = get_data_retention_days(age)
        assert result == expected_days

    @pytest.mark.parametrize("age", [3, 7, 12, 13, 15, 16])
    def test_get_data_retention_days_function_disabled(
        self, mock_coppa_disabled, age
    ):
        """Test global get_data_retention_days function when COPPA is disabled."""
        result = get_data_retention_days(age)
        assert result == 365 * 2

    def test_validate_child_age_function_enabled(self, mock_coppa_enabled):
        """Test global validate_child_age function when COPPA is enabled."""
        result = validate_child_age(7)
        assert isinstance(result, COPPAValidationResult)
        assert result.is_coppa_subject is True
        assert result.compliance_level == COPPAComplianceLevel.UNDER_COPPA

    def test_validate_child_age_function_disabled(self, mock_coppa_disabled):
        """Test global validate_child_age function when COPPA is disabled."""
        result = validate_child_age(7)
        assert isinstance(result, COPPAValidationResult)
        assert result.is_coppa_subject is False
        assert (
            result.compliance_level == COPPAComplianceLevel.GENERAL_PROTECTION
        )


class TestCOPPAValidatorGlobalInstance:
    """Test global COPPA validator instance."""

    def test_global_validator_instance(self):
        """Test that global validator instance is created."""
        assert coppa_validator is not None
        assert isinstance(coppa_validator, COPPAValidator)

    def test_global_validator_consistency(self):
        """Test that global validator instance is consistent."""
        validator1 = coppa_validator
        validator2 = coppa_validator
        assert validator1 is validator2


class TestCOPPAValidatorEdgeCases:
    """Test edge cases and error conditions."""

    @pytest.fixture
    def validator(self):
        """Create a COPPAValidator instance."""
        return COPPAValidator()

    @pytest.fixture
    def mock_coppa_enabled(self):
        """Mock COPPA enabled configuration."""
        with patch(
            "src.infrastructure.security.coppa_validator.is_coppa_enabled"
        ) as mock:
            mock.return_value = True
            yield mock

    def test_validator_cache_initialization(self, validator):
        """Test that validator initializes with empty cache."""
        assert validator._validation_cache == {}

    def test_special_protections_structure(
        self, validator, mock_coppa_enabled
    ):
        """Test that special protections have correct structure."""
        result = validator.validate_age_compliance(7)

        expected_keys = {
            "enhanced_content_filtering",
            "restricted_data_sharing",
            "parental_oversight_required",
            "anonymized_analytics_only",
            "encrypted_storage_required",
            "audit_trail_required",
        }

        assert set(result.special_protections.keys()) == expected_keys
        assert all(
            isinstance(v, bool) for v in result.special_protections.values()
        )

    def test_age_boundary_conditions(self, validator, mock_coppa_enabled):
        """Test age boundary conditions."""
        # Test exactly at COPPA limit
        result_12 = validator.validate_age_compliance(12)
        assert result_12.is_coppa_subject is True

        result_13 = validator.validate_age_compliance(13)
        assert result_13.is_coppa_subject is False

        # Test minimum age
        result_3 = validator.validate_age_compliance(3)
        assert result_3.is_coppa_subject is True

        # Test just below minimum
        with pytest.raises(ValueError):
            validator.validate_age_compliance(2)

    def test_logging_integration(self, validator, mock_coppa_enabled):
        """Test that validation includes logging."""
        with patch(
            "src.infrastructure.security.coppa_validator.logger"
        ) as mock_logger:
            validator.validate_age_compliance(7)
            mock_logger.info.assert_called_once()

            # Check log message format
            log_call = mock_logger.info.call_args[0][0]
            assert "COPPA validation completed" in log_call
            assert "age_group=" in log_call
            assert "consent_required=" in log_call
            assert "retention_days=" in log_call

    def test_error_logging_integration(self, validator, mock_coppa_enabled):
        """Test error logging for invalid ages."""
        with patch(
            "src.infrastructure.security.coppa_validator.logger"
        ) as mock_logger:
            result = validator.is_coppa_subject(-1)
            assert result is True
            mock_logger.warning.assert_called_once()

            log_call = mock_logger.warning.call_args[0][0]
            assert "Invalid age for COPPA check" in log_call

    def test_data_retention_error_handling(
        self, validator, mock_coppa_enabled
    ):
        """Test data retention error handling."""
        with patch(
            "src.infrastructure.security.coppa_validator.logger"
        ) as mock_logger:
            result = validator.get_data_retention_period(-1)
            assert result == 90  # COPPA_RETENTION_DAYS
            mock_logger.warning.assert_called_once()

    def test_constants_immutability(self, validator):
        """Test that COPPA constants are properly defined."""
        # These should be class constants, not instance variables
        assert COPPAValidator.COPPA_AGE_LIMIT == 13
        assert COPPAValidator.MIN_CHILD_AGE == 3
        assert COPPAValidator.MAX_CHILD_AGE == 13
        assert COPPAValidator.COPPA_RETENTION_DAYS == 90
        assert COPPAValidator.TRANSITION_RETENTION_DAYS == 365

    def test_validation_result_type_consistency(
        self, validator, mock_coppa_enabled
    ):
        """Test that validation result types are consistent."""
        result = validator.validate_age_compliance(7)

        assert isinstance(result.is_coppa_subject, bool)
        assert isinstance(result.compliance_level, COPPAComplianceLevel)
        assert isinstance(result.parental_consent_required, bool)
        assert isinstance(result.data_retention_days, int)
        assert isinstance(result.special_protections, dict)
        assert isinstance(result.age_verified, bool)

        # Check that all special protections are boolean
        for (
            protection_name,
            protection_value,
        ) in result.special_protections.items():
            assert isinstance(protection_name, str)
            assert isinstance(protection_value, bool)

    @pytest.mark.parametrize("age", [3, 7, 12, 13, 15, 16])
    def test_validation_idempotency(self, validator, mock_coppa_enabled, age):
        """Test that validation is idempotent."""
        result1 = validator.validate_age_compliance(age)
        result2 = validator.validate_age_compliance(age)

        assert result1.is_coppa_subject == result2.is_coppa_subject
        assert result1.compliance_level == result2.compliance_level
        assert (
            result1.parental_consent_required
            == result2.parental_consent_required
        )
        assert result1.data_retention_days == result2.data_retention_days
        assert result1.special_protections == result2.special_protections
        assert result1.age_verified == result2.age_verified

    def test_coppa_disabled_logging(self, validator, mock_coppa_disabled):
        """Test logging when COPPA is disabled."""
        with patch(
            "src.infrastructure.security.coppa_validator.logger"
        ) as mock_logger:
            validator.validate_age_compliance(7)
            mock_logger.debug.assert_called_once()

            log_call = mock_logger.debug.call_args[0][0]
            assert "COPPA compliance disabled" in log_call

    def test_age_validation_with_config_mock(self, validator):
        """Test age validation with configuration mocking."""
        with patch(
            "src.infrastructure.security.coppa_validator.is_coppa_enabled"
        ) as mock_enabled:
            mock_enabled.return_value = True

            result = validator.validate_age_compliance(7)
            assert result.is_coppa_subject is True

            mock_enabled.return_value = False
            result = validator.validate_age_compliance(7)
            assert result.is_coppa_subject is False

    def test_strict_validation_parameter(self, validator, mock_coppa_enabled):
        """Test strict_validation parameter behavior."""
        # Should raise with strict validation
        with pytest.raises(ValueError):
            validator.validate_age_compliance(17, strict_validation=True)

        # Should not raise without strict validation
        result = validator.validate_age_compliance(17, strict_validation=False)
        assert (
            result.compliance_level == COPPAComplianceLevel.GENERAL_PROTECTION
        )

    def test_transition_age_range(self, validator, mock_coppa_enabled):
        """Test transition age range (13-15) handling."""
        for age in [13, 14, 15]:
            result = validator.validate_age_compliance(age)
            assert (
                result.compliance_level
                == COPPAComplianceLevel.COPPA_TRANSITION
            )
            assert result.is_coppa_subject is False
            assert result.parental_consent_required is False
            assert result.data_retention_days == 365
            assert (
                result.special_protections["enhanced_content_filtering"]
                is True
            )
            assert (
                result.special_protections["restricted_data_sharing"] is False
            )
