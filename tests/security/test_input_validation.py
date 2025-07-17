"""
Security tests for input validation
"""

import pytest
from pydantic import ValidationError

from src.presentation.api.endpoints.children.models import (
    ChildCreateRequest,
    ChildUpdateRequest,
    validate_child_data,
)


class TestChildModelValidation:
    """Test child model input validation security."""

    def test_valid_child_creation(self):
        """Test valid child creation request."""
        request = ChildCreateRequest(
            name="Alice", age=7, interests=["reading", "animals"], language="en"
        )
        assert request.name == "Alice"
        assert request.age == 7
        assert "reading" in request.interests

    def test_sql_injection_in_name_blocked(self):
        """Test that SQL injection patterns in names are blocked."""
        with pytest.raises(ValidationError, match="prohibited patterns"):
            ChildCreateRequest(name="Alice'; DROP TABLE children; --", age=7)

    def test_xss_in_name_blocked(self):
        """Test that XSS patterns in names are blocked."""
        with pytest.raises(ValidationError, match="invalid characters"):
            ChildCreateRequest(
                name="Alice<script>alert('xss')</script>", age=7)

    def test_dangerous_characters_blocked(self):
        """Test that dangerous characters are blocked."""
        dangerous_names = [
            "Alice & Bob",
            'Alice "quoted"',
            "Alice's name",
            "Alice\x00null",
            "Alice<test>",
            "Alice>test",
        ]

        for name in dangerous_names:
            with pytest.raises(ValidationError, match="invalid characters"):
                ChildCreateRequest(name=name, age=7)

    def test_empty_name_blocked(self):
        """Test that empty names are blocked."""
        with pytest.raises(ValidationError, match="cannot be empty"):
            ChildCreateRequest(name="", age=7)

        with pytest.raises(ValidationError, match="cannot be empty"):
            ChildCreateRequest(name="   ", age=7)

    def test_coppa_age_validation(self):
        """Test COPPA compliance age validation."""
        # Valid ages
        for age in [1, 7, 13]:
            request = ChildCreateRequest(name="Test", age=age)
            assert request.age == age

        # Invalid ages
        with pytest.raises(ValidationError):
            ChildCreateRequest(name="Test", age=0)

        with pytest.raises(ValidationError):
            ChildCreateRequest(name="Test", age=14)

        with pytest.raises(ValidationError):
            ChildCreateRequest(name="Test", age=-1)

    def test_interests_validation(self):
        """Test interests list validation."""
        # Valid interests
        request = ChildCreateRequest(
            name="Test", age=7, interests=["reading", "animals", "music"]
        )
        assert len(request.interests) == 3

        # Too many interests
        with pytest.raises(ValidationError, match="Maximum.*interests allowed"):
            ChildCreateRequest(
                name="Test", age=7, interests=[f"interest_{i}" for i in range(25)]
            )

        # Invalid interest content
        with pytest.raises(ValidationError, match="invalid characters"):
            ChildCreateRequest(
                name="Test", age=7, interests=["reading", "animals<script>", "music"]
            )

        # Too long interest
        with pytest.raises(ValidationError, match="too long"):
            ChildCreateRequest(
                # Over 50 character limit
                name="Test", age=7, interests=["a" * 60]
            )

        # Non-string interest
        with pytest.raises(ValidationError, match="must be strings"):
            ChildCreateRequest(
                name="Test", age=7, interests=[
                    "reading", 123, "music"])

    def test_language_validation(self):
        """Test language validation."""
        # Valid languages
        for lang in ["en", "ar", "fr", "es", "de"]:
            request = ChildCreateRequest(name="Test", age=7, language=lang)
            assert request.language == lang

        # Invalid language
        with pytest.raises(ValidationError, match="must be one of"):
            ChildCreateRequest(name="Test", age=7, language="invalid")

    def test_name_sanitization(self):
        """Test that names are properly sanitized."""
        request = ChildCreateRequest(name="  Alice  ", age=7)
        assert request.name == "Alice"  # Whitespace stripped

    def test_interests_sanitization(self):
        """Test that interests are properly sanitized."""
        request = ChildCreateRequest(
            name="Test", age=7, interests=["  reading  ", "", "  animals  ", "   "]
        )
        # Empty interests should be filtered out, whitespace trimmed
        assert request.interests == ["reading", "animals"]


class TestChildUpdateValidation:
    """Test child update model validation."""

    def test_valid_update(self):
        """Test valid update request."""
        request = ChildUpdateRequest(name="Alice Updated", age=8)
        assert request.name == "Alice Updated"
        assert request.age == 8

    def test_none_values_allowed(self):
        """Test that None values are allowed for optional fields."""
        request = ChildUpdateRequest(name=None, age=None)
        assert request.name is None
        assert request.age is None

    def test_sql_injection_blocked_in_update(self):
        """Test SQL injection protection in updates."""
        with pytest.raises(ValidationError, match="prohibited patterns"):
            ChildUpdateRequest(name="Alice'; UPDATE children SET age=999; --")

    def test_update_name_sanitization(self):
        """Test name sanitization in updates."""
        request = ChildUpdateRequest(name="  Bob  ")
        assert request.name == "Bob"


class TestGeneralValidation:
    """Test general validation functions."""

    def test_validate_child_data_function(self):
        """Test the validate_child_data function."""
        # Valid data
        valid_data = {
            "name": "Alice",
            "age": 7,
            "interests": ["reading"],
            "language": "en",
        }
        result = validate_child_data(valid_data)
        assert result == valid_data

        # Invalid age
        with pytest.raises(ValueError, match="Age must be between"):
            validate_child_data({"age": 0})

        with pytest.raises(ValueError, match="Age must be between"):
            validate_child_data({"age": 15})

        # Invalid name
        with pytest.raises(ValueError, match="cannot be empty"):
            validate_child_data({"name": ""})

        with pytest.raises(ValueError, match="cannot exceed.*characters"):
            validate_child_data({"name": "a" * 60})

        # Invalid interests
        with pytest.raises(ValueError, match="must be a list"):
            validate_child_data({"interests": "not a list"})

        with pytest.raises(ValueError, match="Maximum.*interests allowed"):
            validate_child_data(
                {"interests": [f"interest_{i}" for i in range(25)]})

        # Invalid language
        with pytest.raises(ValueError, match="must be one of"):
            validate_child_data({"language": "invalid"})


class TestSecurityEdgeCases:
    """Test security edge cases and attack vectors."""

    def test_unicode_attacks(self):
        """Test unicode-based attacks."""
        # Unicode normalization attacks
        with pytest.raises(ValidationError):
            ChildCreateRequest(name="Alice\u202e\u0338", age=7)

    def test_null_byte_injection(self):
        """Test null byte injection attempts."""
        with pytest.raises(ValidationError, match="invalid characters"):
            ChildCreateRequest(name="Alice\x00.txt", age=7)

    def test_very_long_inputs(self):
        """Test very long inputs that could cause DoS."""
        # Name too long
        with pytest.raises(ValidationError):
            ChildCreateRequest(name="A" * 1000, age=7)

        # Too many interests
        with pytest.raises(ValidationError):
            ChildCreateRequest(name="Test", age=7, interests=["test"] * 1000)

    def test_nested_injection_attempts(self):
        """Test nested injection attempts in interests."""
        malicious_interests = [
            "reading",
            "'; DROP TABLE users; --",
            "<script>alert('xss')</script>",
            "javascript:void(0)",
            "data:text/html,<script>alert('xss')</script>",
        ]

        with pytest.raises(ValidationError):
            ChildCreateRequest(
                name="Test",
                age=7,
                interests=malicious_interests)

    def test_case_insensitive_sql_patterns(self):
        """Test that SQL injection patterns are caught regardless of case."""
        sql_patterns = [
            "Alice'; drop table children; --",
            "Alice'; DROP TABLE children; --",
            "Alice'; DrOp TaBlE children; --",
            "Alice'; DELETE FROM children; --",
            "Alice'; delete from children; --",
        ]

        for pattern in sql_patterns:
            with pytest.raises(ValidationError, match="prohibited patterns"):
                ChildCreateRequest(name=pattern, age=7)

    def test_preferences_security(self):
        """Test that preferences dict doesn't allow dangerous content."""
        # This would need additional validation in a real implementation
        request = ChildCreateRequest(
            name="Test", age=7, preferences={"theme": "blue", "notifications": True}
        )
        assert request.preferences["theme"] == "blue"

        # In a real implementation, we'd also validate preference values
        # for safety, but this basic test ensures the structure works


if __name__ == "__main__":
    pytest.main([__file__])
