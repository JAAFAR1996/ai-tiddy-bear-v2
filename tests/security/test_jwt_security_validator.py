"""
Comprehensive test suite for JWT Security Validator.

Tests both strong and weak JWT secrets to ensure the system fails securely
when encountering insufficient security.
"""

import secrets

import pytest

from src.infrastructure.security.auth.jwt_security_validator import JWTSecurityValidator


class TestJWTSecurityValidator:
    """Test suite for JWT security validation."""

    def test_valid_strong_secret_passes(self):
        """Test that a cryptographically strong secret passes validation."""
        # Generate a strong secret using cryptographic randomness
        strong_secret = secrets.token_urlsafe(64)  # 86 characters base64

        result = JWTSecurityValidator.validate_jwt_secret(strong_secret)
        assert result is True

    def test_minimum_length_enforcement(self):
        """Test that secrets below 64 characters are rejected."""
        short_secrets = [
            "",  # Empty
            "short",  # Very short
            "a" * 32,  # Old minimum length
            "a" * 63,  # Just below new minimum
        ]

        for secret in short_secrets:
            with pytest.raises(ValueError, match="must be at least 64 characters"):
                JWTSecurityValidator.validate_jwt_secret(secret)

    def test_entropy_validation(self):
        """Test that low-entropy secrets are rejected."""
        low_entropy_secrets = [
            "a" * 64,  # All same character
            "ababababababababababababababababababababababababababababababab",  # Repeated pattern
            "1111111111111111111111111111111111111111111111111111111111111111",  # All same digit
            "AAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAA",  # All same uppercase
        ]

        for secret in low_entropy_secrets:
            with pytest.raises(ValueError, match="insufficient entropy"):
                JWTSecurityValidator.validate_jwt_secret(secret)

    def test_weak_pattern_detection(self):
        """Test detection of weak patterns in secrets."""
        weak_secrets = [
            # Repeated characters
            "aaaa" + "b" * 60,
            "1111" + "x" * 60,
            # Common sequences
            "abcdef" + "x" * 58,
            "123456" + "y" * 58,
            "qwerty" + "z" * 58,
            # Common words
            "password" + "x" * 56,
            "secretkey" + "y" * 55,
            "tokenauth" + "z" * 55,
            # Development terms
            "testkey" + "a" * 57,
            "devtoken" + "b" * 56,
            "demoauth" + "c" * 56,
            # Long alphanumeric runs (insufficient complexity)
            "abcdefghijklmnopqrstuvwxyz" + "0123456789" * 4,
        ]

        for secret in weak_secrets:
            with pytest.raises(
                ValueError,
                match="weak or guessable patterns|insufficient character diversity",
            ):
                JWTSecurityValidator.validate_jwt_secret(secret)

    def test_character_diversity_requirement(self):
        """Test that secrets must have diverse character sets."""
        non_diverse_secrets = [
            # Only lowercase
            "abcdefghijklmnopqrstuvwxyzabcdefghijklmnopqrstuvwxyzabcdefghij",
            # Only uppercase
            "ABCDEFGHIJKLMNOPQRSTUVWXYZABCDEFGHIJKLMNOPQRSTUVWXYZABCDEFGHIJ",
            # Only digits
            "0123456789012345678901234567890123456789012345678901234567890123",
            # Only letters (mixed case but no digits/symbols)
            "AbCdEfGhIjKlMnOpQrStUvWxYzAbCdEfGhIjKlMnOpQrStUvWxYzAbCdEfGhIj",
        ]

        for secret in non_diverse_secrets:
            with pytest.raises(ValueError, match="insufficient character diversity"):
                JWTSecurityValidator.validate_jwt_secret(secret)

    def test_sequential_pattern_detection(self):
        """Test detection of sequential patterns."""
        sequential_secrets = [
            # Alphabet sequences
            "abcdefgh" + "x" * 56,
            "ABCDEFGH" + "y" * 56,
            # Numeric sequences
            "12345678" + "z" * 56,
            "87654321" + "a" * 56,
            # Keyboard sequences
            "qwertyui" + "b" * 56,
            "asdfghjk" + "c" * 56,
        ]

        for secret in sequential_secrets:
            with pytest.raises(ValueError, match="sequential patterns"):
                JWTSecurityValidator.validate_jwt_secret(secret)

    def test_shannon_entropy_calculation(self):
        """Test Shannon entropy calculation accuracy."""
        # Perfect entropy (all characters equally likely)
        uniform_string = "".join(chr(i) for i in range(32, 127))  # All printable ASCII
        entropy = JWTSecurityValidator._calculate_shannon_entropy(uniform_string)
        assert entropy > 6.0  # Should be very high

        # Low entropy (repeated character)
        low_entropy_string = "a" * 100
        entropy = JWTSecurityValidator._calculate_shannon_entropy(low_entropy_string)
        assert entropy == 0.0  # Should be zero

        # Empty string
        entropy = JWTSecurityValidator._calculate_shannon_entropy("")
        assert entropy == 0.0

    def test_strong_secrets_with_good_entropy(self):
        """Test various strong secrets that should pass."""
        strong_secrets = [
            # Cryptographically generated
            secrets.token_urlsafe(64),
            secrets.token_hex(64),
            # Mixed character sets with good entropy
            "Kj8#mN2$qP9&xL5*eR7@tY4!wE6%uI3^oU1+aS0-dF8#gH7&jK5*lZ2$vB4!",
            "9mX#7nV$2kL@8pQ!6rT&5yU*4eR^3wE%1qA+0sD-9fG#8hJ&7lK*6zX$5cV!",
            # Base64-like with good randomness
            "Ab3D+/9mNq7X5kLp2E8rT6yU4wQ1sA0cF+/8vB3gH7jK5zX9nM2qP6eR4tY!",
        ]

        for secret in strong_secrets:
            if len(secret) >= 64:  # Ensure minimum length
                result = JWTSecurityValidator.validate_jwt_secret(secret)
                assert result is True

    def test_input_validation(self):
        """Test input validation and error handling."""
        # Non-string input
        with pytest.raises(ValueError, match="must be a string"):
            JWTSecurityValidator.validate_jwt_secret(None)

        with pytest.raises(ValueError, match="must be a string"):
            JWTSecurityValidator.validate_jwt_secret(123)

        with pytest.raises(ValueError, match="must be a string"):
            JWTSecurityValidator.validate_jwt_secret([])

    def test_edge_cases(self):
        """Test edge cases and boundary conditions."""
        # Exactly 64 characters with good entropy and diversity
        exactly_64_chars = (
            "Aj3F$9mL&6pQ*2eR#8tY!5uI%7kN^4wE+1xS-0cV$9bG&6hJ*3zX#8nM!5qP"
        )
        assert len(exactly_64_chars) == 64
        result = JWTSecurityValidator.validate_jwt_secret(exactly_64_chars)
        assert result is True

    def test_incremental_sequence_detection(self):
        """Test detection of incremental sequences."""
        # Test numeric incremental sequences
        assert JWTSecurityValidator._is_incremental_sequence("1234") is True
        assert JWTSecurityValidator._is_incremental_sequence("9876") is True
        assert JWTSecurityValidator._is_incremental_sequence("1357") is False

        # Test alphabetic incremental sequences
        assert JWTSecurityValidator._is_incremental_sequence("abcd") is True
        assert JWTSecurityValidator._is_incremental_sequence("zyxw") is True
        assert JWTSecurityValidator._is_incremental_sequence("aceg") is False

        # Test mixed sequences (should return False)
        assert JWTSecurityValidator._is_incremental_sequence("1a2b") is False
        assert JWTSecurityValidator._is_incremental_sequence("ab12") is False


class TestJWTSecuritySystemIntegration:
    """Integration tests to verify system behavior with JWT security."""

    def test_system_fails_with_weak_jwt_secret(self):
        """Test that the system fails to start with weak JWT secrets."""
        from unittest.mock import Mock

        from src.infrastructure.security.auth.token_service import TokenService

        # Mock settings with weak secret
        mock_settings = Mock()
        mock_settings.security = Mock()
        mock_settings.security.SECRET_KEY = "weak_secret_12345"  # Too short and weak
        mock_settings.security.JWT_ALGORITHM = "HS256"
        mock_settings.security.ACCESS_TOKEN_EXPIRE_MINUTES = 30
        mock_settings.security.REFRESH_TOKEN_EXPIRE_DAYS = 7

        # System should fail to initialize
        with pytest.raises(ValueError, match="Critical security error"):
            TokenService(mock_settings)

    def test_system_starts_with_strong_jwt_secret(self):
        """Test that the system starts successfully with strong JWT secrets."""
        from unittest.mock import Mock

        from src.infrastructure.security.auth.token_service import TokenService

        # Mock settings with strong secret
        mock_settings = Mock()
        mock_settings.security = Mock()
        mock_settings.security.SECRET_KEY = secrets.token_urlsafe(64)  # Strong secret
        mock_settings.security.JWT_ALGORITHM = "HS256"
        mock_settings.security.ACCESS_TOKEN_EXPIRE_MINUTES = 30
        mock_settings.security.REFRESH_TOKEN_EXPIRE_DAYS = 7

        # System should initialize successfully
        token_service = TokenService(mock_settings)
        assert token_service is not None
        assert token_service.secret_key == mock_settings.security.SECRET_KEY


def generate_test_secrets_report():
    """Generate a report of test results for different secret types."""
    test_results = []

    # Test various secret types
    test_cases = [
        ("Empty string", ""),
        ("Short secret", "short123"),
        ("Old minimum length", "a" * 32),
        ("Low entropy", "a" * 64),
        ("Sequential", "abcdefgh" + "x" * 56),
        ("Weak pattern", "password" + "x" * 56),
        ("Strong secret", secrets.token_urlsafe(64)),
    ]

    for name, secret in test_cases:
        try:
            JWTSecurityValidator.validate_jwt_secret(secret)
            test_results.append((name, "PASSED", "Secret accepted"))
        except ValueError as e:
            test_results.append((name, "FAILED", str(e)))

    return test_results


if __name__ == "__main__":
    # Generate test report
    results = generate_test_secrets_report()
    print("\n🔐 JWT Security Validation Test Report")
    print("=" * 60)
    for name, status, message in results:
        print(f"{name:20} | {status:6} | {message[:40]}...")
