"""
Comprehensive tests for JWT security validator.

Tests cryptographic validation of JWT secrets for child safety compliance.
Ensures proper rejection of weak secrets and acceptance of strong ones.
"""

import secrets
import string

import pytest

from src.infrastructure.security.validators.jwt_security_validator import (
    JWTSecurityValidator,
    jwt_security_validator,
)


class TestJWTSecurityValidator:
    """Test comprehensive JWT secret validation for child safety."""

    def test_strong_secret_passes_validation(self):
        """Test that a strong cryptographic secret passes all validation."""
        # Generate a strong 64-character secret with high entropy
        strong_secret = secrets.token_urlsafe(64)

        # Should not raise any exception
        jwt_security_validator.validate_jwt_secret(strong_secret)

    def test_secret_too_short_fails(self):
        """Test that secrets shorter than 64 characters fail validation."""
        short_secret = "a" * 63  # One character short

        with pytest.raises(
            ValueError, match="JWT secret must be at least 64 characters"
        ):
            jwt_security_validator.validate_jwt_secret(short_secret)

    def test_empty_secret_fails(self):
        """Test that empty or None secrets fail validation."""
        with pytest.raises(ValueError, match="JWT secret cannot be empty"):
            jwt_security_validator.validate_jwt_secret("")

        with pytest.raises(ValueError, match="JWT secret cannot be empty"):
            jwt_security_validator.validate_jwt_secret(None)

    def test_development_keys_fail(self):
        """Test that development/placeholder keys fail validation."""
        development_keys = [
            "development_secret_key_that_is_64_characters_long_for_testing_only",
            "test_secret_key_that_is_exactly_64_characters_long_for_development",
            "placeholder_jwt_secret_key_that_meets_length_requirements_exactly",
            "dummy_secret_key_for_development_that_is_exactly_64_chars_long_ok",
            "sample_jwt_secret_key_that_is_exactly_64_characters_long_for_demo",
        ]

        for dev_key in development_keys:
            with pytest.raises(ValueError, match="development.*key"):
                jwt_security_validator.validate_jwt_secret(dev_key)

    def test_weak_patterns_fail(self):
        """Test that secrets with weak patterns fail validation."""
        weak_patterns = [
            "1234567890" * 7,  # Repeated digits (70 chars)
            "abcdefghij" * 7,  # Repeated sequence (70 chars)
            "a" * 70,  # Single character repeated
            "12345678901234567890123456789012345678901234567890123456789012345678901234567890",  # Sequential
            "password123456789012345678901234567890123456789012345678901234567890",  # Common word
        ]

        for weak_pattern in weak_patterns:
            with pytest.raises(ValueError, match="weak pattern"):
                jwt_security_validator.validate_jwt_secret(weak_pattern)

    def test_low_entropy_fails(self):
        """Test that secrets with low Shannon entropy fail validation."""
        # Create a secret with low entropy (repeated characters)
        low_entropy_secret = ("ab" * 32) + ("cd" * 16)  # 64 chars but low entropy

        with pytest.raises(ValueError, match="insufficient entropy"):
            jwt_security_validator.validate_jwt_secret(low_entropy_secret)

    def test_shannon_entropy_calculation(self):
        """Test Shannon entropy calculation accuracy."""
        validator = JWTSecurityValidator()

        # Test uniform distribution (maximum entropy for 2 symbols)
        uniform_string = "a" * 32 + "b" * 32
        entropy = validator._calculate_shannon_entropy(uniform_string)
        assert 0.9 <= entropy <= 1.1  # Should be close to 1.0

        # Test single character (minimum entropy)
        single_char = "a" * 64
        entropy = validator._calculate_shannon_entropy(single_char)
        assert entropy == 0.0

    def test_cryptographic_randomness_validation(self):
        """Test cryptographic randomness validation."""
        validator = JWTSecurityValidator()

        # Strong random secret should pass
        strong_secret = secrets.token_urlsafe(64)
        assert validator._validate_cryptographic_randomness(strong_secret) is True

        # Weak predictable pattern should fail
        weak_secret = "1234567890" * 7
        assert validator._validate_cryptographic_randomness(weak_secret) is False

    def test_pattern_detection(self):
        """Test weak pattern detection."""
        validator = JWTSecurityValidator()

        # Test various weak patterns
        patterns_to_test = [
            (
                "1234567890123456789012345678901234567890123456789012345678901234",
                True,
            ),  # Sequential
            (
                "abcdefghijklmnopqrstuvwxyzabcdefghijklmnopqrstuvwxyzabcdefghijkl",
                True,
            ),  # Alphabet
            (
                "password1234567890123456789012345678901234567890123456789012345",
                True,
            ),  # Common word
            (secrets.token_urlsafe(64), False),  # Strong random
        ]

        for pattern, should_be_weak in patterns_to_test:
            result = validator._check_weak_patterns(pattern)
            if should_be_weak:
                assert (
                    result is True
                ), f"Pattern should be detected as weak: {pattern[:20]}..."
            else:
                assert (
                    result is False
                ), f"Pattern should not be detected as weak: {pattern[:20]}..."

    def test_comprehensive_validation_with_strong_secret(self):
        """Test complete validation flow with a strong secret."""
        # Generate a cryptographically strong secret
        alphabet = string.ascii_letters + string.digits + "!@#$%^&*()_+-="
        strong_secret = "".join(secrets.choice(alphabet) for _ in range(80))

        # Should pass all validation checks
        jwt_security_validator.validate_jwt_secret(strong_secret)

    def test_validation_error_messages(self):
        """Test that validation error messages are descriptive."""
        test_cases = [
            ("", "empty"),
            ("short", "64 characters"),
            (
                "development_key_that_is_64_characters_long_for_testing_purposes",
                "development",
            ),
            ("a" * 70, "weak pattern"),
            ("ab" * 35, "insufficient entropy"),  # Low entropy but 70 chars
        ]

        for secret, expected_message_part in test_cases:
            with pytest.raises(ValueError) as exc_info:
                jwt_security_validator.validate_jwt_secret(secret)
            assert expected_message_part in str(exc_info.value).lower()

    def test_singleton_instance(self):
        """Test that jwt_security_validator is a singleton instance."""
        validator1 = jwt_security_validator
        validator2 = jwt_security_validator
        assert validator1 is validator2

    def test_real_world_weak_secrets(self):
        """Test validation against real-world weak secret examples."""
        weak_secrets = [
            # Common weak patterns extended to meet length requirement
            "admin123456789012345678901234567890123456789012345678901234567890",
            "secret123456789012345678901234567890123456789012345678901234567890",
            "mysecretkey123456789012345678901234567890123456789012345678901234",
            "jwt_secret_key_123456789012345678901234567890123456789012345678901",
            # Keyboard patterns
            "qwertyuiopasdfghjklzxcvbnmqwertyuiopasdfghjklzxcvbnmqwertyuiopas",
            # Repeated words
            "supersecret" * 6 + "supe",  # 64+ chars
            # Base64 of simple strings
            "cGFzc3dvcmQxMjM0NTY3ODkwMTIzNDU2Nzg5MDEyMzQ1Njc4OTAxMjM0NTY3ODkw",
        ]

        for weak_secret in weak_secrets:
            with pytest.raises(ValueError):
                jwt_security_validator.validate_jwt_secret(weak_secret)

    def test_edge_case_lengths(self):
        """Test validation at exact length boundaries."""
        # Exactly 64 characters - should pass if strong
        exactly_64 = secrets.token_urlsafe(48)  # This generates ~64 chars
        if len(exactly_64) >= 64:
            jwt_security_validator.validate_jwt_secret(exactly_64)

        # 63 characters - should fail
        exactly_63 = "a" * 63
        with pytest.raises(ValueError, match="64 characters"):
            jwt_security_validator.validate_jwt_secret(exactly_63)


class TestJWTValidatorIntegration:
    """Integration tests for JWT validator with application components."""

    def test_validator_integration_with_settings(self):
        """Test that validator integrates properly with settings validation."""
        from src.infrastructure.config.security.security_settings import (
            SecuritySettings,
        )

        # Test with strong secret
        strong_secret = secrets.token_urlsafe(64)
        settings_data = {
            "SECRET_KEY": strong_secret,
            "JWT_SECRET_KEY": strong_secret,
            "JWT_ALGORITHM": "HS256",
            "JWT_ACCESS_TOKEN_EXPIRE_MINUTES": 30,
        }

        # Should not raise any validation errors
        settings = SecuritySettings(**settings_data)
        assert settings.JWT_SECRET_KEY == strong_secret

    def test_validator_integration_with_token_service(self):
        """Test that validator integrates with token service initialization."""
        from src.infrastructure.config.security.security_settings import (
            SecuritySettings,
        )
        from src.infrastructure.security.auth.token_service import TokenService

        # Create settings with strong JWT secret
        strong_secret = secrets.token_urlsafe(64)
        settings = SecuritySettings(
            SECRET_KEY=strong_secret,
            JWT_SECRET_KEY=strong_secret,
            JWT_ALGORITHM="HS256",
            JWT_ACCESS_TOKEN_EXPIRE_MINUTES=30,
        )

        # TokenService should initialize without errors
        token_service = TokenService(settings)
        assert token_service is not None


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
