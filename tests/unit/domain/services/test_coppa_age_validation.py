"""Tests for COPPA Age Validation Service
Testing centralized age validation for COPPA compliance.
"""

from datetime import date
from freezegun import freeze_time

from src.domain.services.coppa_age_validation import (
    AgeValidationResult,
    COPPAAgeValidator,
    is_age_coppa_compliant,
    validate_child_age,
)


class TestAgeValidationResult:
    """Test the AgeValidationResult enum."""

    def test_age_validation_result_values(self):
        """Test that all expected validation results exist."""
        assert AgeValidationResult.VALID_CHILD.value == "valid_child"
        assert AgeValidationResult.VALID_TEEN.value == "valid_teen"
        assert AgeValidationResult.VALID_ADULT.value == "valid_adult"
        assert AgeValidationResult.TOO_YOUNG.value == "too_young"
        assert AgeValidationResult.INVALID_AGE.value == "invalid_age"
        assert AgeValidationResult.MISSING_BIRTHDATE.value == "missing_birthdate"


class TestCOPPAAgeValidator:
    """Test the COPPA Age Validator class."""

    def test_class_constants(self):
        """Test that class constants are properly defined."""
        assert COPPAAgeValidator.MINIMUM_AGE == 3
        assert COPPAAgeValidator.COPPA_AGE_LIMIT == 13
        assert COPPAAgeValidator.ADULT_AGE == 18

    # validate_age tests
    def test_validate_age_none(self):
        """Test validation with None age."""
        result = COPPAAgeValidator.validate_age(None)
        assert result == AgeValidationResult.INVALID_AGE

    def test_validate_age_negative(self):
        """Test validation with negative age."""
        result = COPPAAgeValidator.validate_age(-1)
        assert result == AgeValidationResult.INVALID_AGE

    def test_validate_age_not_integer(self):
        """Test validation with non-integer age."""
        result = COPPAAgeValidator.validate_age(5.5)
        assert result == AgeValidationResult.INVALID_AGE

    def test_validate_age_too_young(self):
        """Test validation for ages below minimum (0-2)."""
        for age in range(0, 3):
            result = COPPAAgeValidator.validate_age(age)
            assert result == AgeValidationResult.TOO_YOUNG

    def test_validate_age_valid_child(self):
        """Test validation for COPPA-applicable children (3-12)."""
        for age in range(3, 13):
            result = COPPAAgeValidator.validate_age(age)
            assert result == AgeValidationResult.VALID_CHILD

    def test_validate_age_valid_teen(self):
        """Test validation for teenagers (13-17)."""
        for age in range(13, 18):
            result = COPPAAgeValidator.validate_age(age)
            assert result == AgeValidationResult.VALID_TEEN

    def test_validate_age_valid_adult(self):
        """Test validation for adults (18+)."""
        for age in [18, 19, 20, 25, 30, 50, 100]:
            result = COPPAAgeValidator.validate_age(age)
            assert result == AgeValidationResult.VALID_ADULT

    # validate_birthdate tests
    @freeze_time("2024-01-15")
    def test_validate_birthdate_none(self):
        """Test validation with None birthdate."""
        result = COPPAAgeValidator.validate_birthdate(None)
        assert result == AgeValidationResult.MISSING_BIRTHDATE

    @freeze_time("2024-01-15")
    def test_validate_birthdate_not_date(self):
        """Test validation with non-date birthdate."""
        result = COPPAAgeValidator.validate_birthdate("2020-01-01")
        assert result == AgeValidationResult.INVALID_AGE

    @freeze_time("2024-01-15")
    def test_validate_birthdate_future(self):
        """Test validation with future birthdate."""
        future_date = date(2025, 1, 1)
        result = COPPAAgeValidator.validate_birthdate(future_date)
        assert result == AgeValidationResult.INVALID_AGE

    @freeze_time("2024-01-15")
    def test_validate_birthdate_valid_child(self):
        """Test validation for child birthdate."""
        # Child who is 5 years old
        birthdate = date(2019, 1, 15)
        result = COPPAAgeValidator.validate_birthdate(birthdate)
        assert result == AgeValidationResult.VALID_CHILD

    @freeze_time("2024-01-15")
    def test_validate_birthdate_birthday_not_occurred(self):
        """Test validation when birthday hasn't occurred this year."""
        # Child born on Jan 20, 2019 (still 4 years old on Jan 15, 2024)
        birthdate = date(2019, 1, 20)
        result = COPPAAgeValidator.validate_birthdate(birthdate)
        assert result == AgeValidationResult.VALID_CHILD

    @freeze_time("2024-01-15")
    def test_validate_birthdate_birthday_occurred(self):
        """Test validation when birthday has occurred this year."""
        # Child born on Jan 10, 2019 (turned 5 on Jan 10, 2024)
        birthdate = date(2019, 1, 10)
        result = COPPAAgeValidator.validate_birthdate(birthdate)
        assert result == AgeValidationResult.VALID_CHILD

    # get_age_from_birthdate tests
    @freeze_time("2024-01-15")
    def test_get_age_from_birthdate_exact_years(self):
        """Test age calculation for exact years."""
        birthdate = date(2020, 1, 15)
        age = COPPAAgeValidator.get_age_from_birthdate(birthdate)
        assert age == 4

    @freeze_time("2024-01-15")
    def test_get_age_from_birthdate_birthday_not_occurred(self):
        """Test age calculation when birthday hasn't occurred."""
        birthdate = date(2020, 1, 20)
        age = COPPAAgeValidator.get_age_from_birthdate(birthdate)
        assert age == 3

    @freeze_time("2024-01-15")
    def test_get_age_from_birthdate_birthday_occurred(self):
        """Test age calculation when birthday has occurred."""
        birthdate = date(2020, 1, 10)
        age = COPPAAgeValidator.get_age_from_birthdate(birthdate)
        assert age == 4

    @freeze_time("2024-02-29")  # Leap year
    def test_get_age_from_birthdate_leap_year(self):
        """Test age calculation with leap year birthdate."""
        birthdate = date(2020, 2, 29)  # Born on leap day
        age = COPPAAgeValidator.get_age_from_birthdate(birthdate)
        assert age == 4

    # requires_parental_consent tests
    def test_requires_parental_consent_child(self):
        """Test parental consent requirement for children."""
        for age in range(3, 13):
            assert COPPAAgeValidator.requires_parental_consent(age) is True

    def test_requires_parental_consent_teen(self):
        """Test parental consent requirement for teens."""
        for age in range(13, 18):
            assert COPPAAgeValidator.requires_parental_consent(age) is True

    def test_requires_parental_consent_adult(self):
        """Test parental consent not required for adults."""
        for age in [18, 19, 20, 25]:
            assert COPPAAgeValidator.requires_parental_consent(age) is False

    def test_requires_parental_consent_invalid_age(self):
        """Test parental consent for invalid ages."""
        assert COPPAAgeValidator.requires_parental_consent(-1) is False
        assert COPPAAgeValidator.requires_parental_consent(0) is False
        assert COPPAAgeValidator.requires_parental_consent(2) is False

    # is_coppa_applicable tests
    def test_is_coppa_applicable_child(self):
        """Test COPPA applicability for children under 13."""
        for age in range(3, 13):
            assert COPPAAgeValidator.is_coppa_applicable(age) is True

    def test_is_coppa_applicable_teen(self):
        """Test COPPA not applicable for teens 13+."""
        for age in range(13, 18):
            assert COPPAAgeValidator.is_coppa_applicable(age) is False

    def test_is_coppa_applicable_adult(self):
        """Test COPPA not applicable for adults."""
        assert COPPAAgeValidator.is_coppa_applicable(18) is False
        assert COPPAAgeValidator.is_coppa_applicable(25) is False

    def test_is_coppa_applicable_invalid_age(self):
        """Test COPPA applicability for invalid ages."""
        assert COPPAAgeValidator.is_coppa_applicable(-1) is False
        assert COPPAAgeValidator.is_coppa_applicable(0) is False
        assert COPPAAgeValidator.is_coppa_applicable(2) is False

    # get_validation_details tests
    def test_get_validation_details_valid_child(self):
        """Test detailed validation for valid child."""
        details = COPPAAgeValidator.get_validation_details(8)

        assert details["age"] == 8
        assert details["validation_result"] == "valid_child"
        assert details["is_valid"] is True
        assert details["requires_parental_consent"] is True
        assert details["coppa_applicable"] is True
        assert details["can_interact"] is True
        assert details["safety_level"] == "high_protection"
        assert "COPPA compliance required" in details["compliance_notes"]

    def test_get_validation_details_valid_teen(self):
        """Test detailed validation for valid teen."""
        details = COPPAAgeValidator.get_validation_details(15)

        assert details["age"] == 15
        assert details["validation_result"] == "valid_teen"
        assert details["is_valid"] is True
        assert details["requires_parental_consent"] is True
        assert details["coppa_applicable"] is False
        assert details["can_interact"] is True
        assert details["safety_level"] == "moderate_protection"
        assert "Parental consent recommended" in details["compliance_notes"]

    def test_get_validation_details_valid_adult(self):
        """Test detailed validation for valid adult."""
        details = COPPAAgeValidator.get_validation_details(20)

        assert details["age"] == 20
        assert details["validation_result"] == "valid_adult"
        assert details["is_valid"] is True
        assert details["requires_parental_consent"] is False
        assert details["coppa_applicable"] is False
        assert details["can_interact"] is True
        assert details["safety_level"] == "standard_protection"
        assert "Standard privacy protection" in details["compliance_notes"]

    def test_get_validation_details_too_young(self):
        """Test detailed validation for too young."""
        details = COPPAAgeValidator.get_validation_details(2)

        assert details["age"] == 2
        assert details["validation_result"] == "too_young"
        assert details["is_valid"] is False
        assert details["requires_parental_consent"] is False
        assert details["coppa_applicable"] is False
        assert details["can_interact"] is False
        assert details["safety_level"] == "blocked"
        assert "Age too young" in details["compliance_notes"]

    def test_get_validation_details_invalid_age(self):
        """Test detailed validation for invalid age."""
        details = COPPAAgeValidator.get_validation_details(None)

        assert details["age"] is None
        assert details["validation_result"] == "invalid_age"
        assert details["is_valid"] is False
        assert details["requires_parental_consent"] is False
        assert details["coppa_applicable"] is False
        assert details["can_interact"] is False
        assert details["safety_level"] == "blocked"
        assert "Invalid age data" in details["compliance_notes"]

    # _get_safety_level tests
    def test_get_safety_level_all_results(self):
        """Test safety level mapping for all validation results."""
        assert (
            COPPAAgeValidator._get_safety_level(AgeValidationResult.VALID_CHILD)
            == "high_protection"
        )
        assert (
            COPPAAgeValidator._get_safety_level(AgeValidationResult.VALID_TEEN)
            == "moderate_protection"
        )
        assert (
            COPPAAgeValidator._get_safety_level(AgeValidationResult.VALID_ADULT)
            == "standard_protection"
        )
        assert (
            COPPAAgeValidator._get_safety_level(AgeValidationResult.TOO_YOUNG)
            == "blocked"
        )
        assert (
            COPPAAgeValidator._get_safety_level(AgeValidationResult.INVALID_AGE)
            == "blocked"
        )
        assert (
            COPPAAgeValidator._get_safety_level(AgeValidationResult.MISSING_BIRTHDATE)
            == "blocked"
        )

    # _get_compliance_notes tests
    def test_get_compliance_notes_all_results(self):
        """Test compliance notes for all validation results."""
        notes = COPPAAgeValidator._get_compliance_notes(AgeValidationResult.VALID_CHILD)
        assert "COPPA compliance required" in notes

        notes = COPPAAgeValidator._get_compliance_notes(AgeValidationResult.VALID_TEEN)
        assert "Parental consent recommended" in notes

        notes = COPPAAgeValidator._get_compliance_notes(AgeValidationResult.VALID_ADULT)
        assert "Standard privacy protection" in notes

        notes = COPPAAgeValidator._get_compliance_notes(AgeValidationResult.TOO_YOUNG)
        assert "Age too young" in notes

        notes = COPPAAgeValidator._get_compliance_notes(AgeValidationResult.INVALID_AGE)
        assert "Invalid age data" in notes

        notes = COPPAAgeValidator._get_compliance_notes(
            AgeValidationResult.MISSING_BIRTHDATE
        )
        assert "Birthdate required" in notes


class TestHelperFunctions:
    """Test the helper functions."""

    def test_validate_child_age(self):
        """Test the validate_child_age helper function."""
        result = validate_child_age(10)

        assert isinstance(result, dict)
        assert result["age"] == 10
        assert result["validation_result"] == "valid_child"
        assert result["is_valid"] is True
        assert result["coppa_applicable"] is True

    def test_validate_child_age_none(self):
        """Test validate_child_age with None."""
        result = validate_child_age(None)

        assert isinstance(result, dict)
        assert result["age"] is None
        assert result["validation_result"] == "invalid_age"
        assert result["is_valid"] is False

    def test_is_age_coppa_compliant(self):
        """Test the is_age_coppa_compliant helper function."""
        # COPPA applies to children under 13
        assert is_age_coppa_compliant(5) is True
        assert is_age_coppa_compliant(12) is True
        assert is_age_coppa_compliant(13) is False
        assert is_age_coppa_compliant(18) is False

    def test_is_age_coppa_compliant_edge_cases(self):
        """Test is_age_coppa_compliant edge cases."""
        assert is_age_coppa_compliant(0) is False  # Too young
        assert is_age_coppa_compliant(3) is True  # Minimum valid age
        assert is_age_coppa_compliant(12) is True  # Last COPPA age
        assert is_age_coppa_compliant(13) is False  # First non-COPPA age
