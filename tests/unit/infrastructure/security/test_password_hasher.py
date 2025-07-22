"""Tests for Password Hasher
Testing secure password hashing and verification using bcrypt.
"""

import threading
import time
from unittest.mock import Mock, patch

import bcrypt
import pytest

from src.infrastructure.security.encryption.password_hasher import PasswordHasher


class TestPasswordHasher:
    """Test the Password Hasher service."""

    @pytest.fixture
    def mock_settings(self):
        """Create mock settings for testing."""
        mock_settings = Mock()
        mock_settings.security = Mock()
        mock_settings.security.PASSWORD_MIN_LENGTH = 8
        mock_settings.security.PASSWORD_HASH_ROUNDS = 12
        return mock_settings

    @pytest.fixture
    def password_hasher(self, mock_settings):
        """Create a password hasher instance with test settings."""
        return PasswordHasher(settings=mock_settings)

    @pytest.fixture
    def production_password_hasher(self):
        """Create a password hasher instance with real settings."""
        return PasswordHasher()

    def test_initialization_with_custom_settings(self, mock_settings):
        """Test password hasher initialization with custom settings."""
        hasher = PasswordHasher(settings=mock_settings)

        assert hasher.settings == mock_settings
        assert hasher.password_min_length == 8
        assert hasher.bcrypt_rounds == 12

    def test_initialization_with_default_settings(self):
        """Test password hasher initialization with default settings."""
        with patch(
            "src.infrastructure.security.password_hasher.get_settings"
        ) as mock_get_settings:
            mock_settings = Mock()
            mock_settings.security.PASSWORD_MIN_LENGTH = 10
            mock_settings.security.PASSWORD_HASH_ROUNDS = 14
            mock_get_settings.return_value = mock_settings

            hasher = PasswordHasher()

            assert hasher.settings == mock_settings
            assert hasher.password_min_length == 10
            assert hasher.bcrypt_rounds == 14

    def test_hash_password_valid_password(self, password_hasher):
        """Test hashing a valid password."""
        password = "securepassword123"

        hashed = password_hasher.hash_password(password)

        # Verify hash characteristics
        assert isinstance(hashed, str)
        assert len(hashed) > 0
        assert hashed != password  # Should not be plaintext
        assert hashed.startswith("$2b$")  # bcrypt hash format

        # Verify the hash can be verified
        assert bcrypt.checkpw(password.encode("utf-8"), hashed.encode("utf-8"))

    def test_hash_password_minimum_length(self, password_hasher):
        """Test hashing password with minimum required length."""
        password = "12345678"  # Exactly 8 characters (minimum)

        hashed = password_hasher.hash_password(password)

        assert isinstance(hashed, str)
        assert len(hashed) > 0
        assert bcrypt.checkpw(password.encode("utf-8"), hashed.encode("utf-8"))

    def test_hash_password_too_short(self, password_hasher):
        """Test hashing password that is too short."""
        password = "1234567"  # 7 characters (below minimum of 8)

        with pytest.raises(
            ValueError, match="Password does not meet security requirements"
        ):
            password_hasher.hash_password(password)

    def test_hash_password_empty_password(self, password_hasher):
        """Test hashing empty password."""
        with pytest.raises(
            ValueError, match="Password does not meet security requirements"
        ):
            password_hasher.hash_password("")

    def test_hash_password_none_password(self, password_hasher):
        """Test hashing None password."""
        with pytest.raises(
            ValueError, match="Password does not meet security requirements"
        ):
            password_hasher.hash_password(None)

    def test_hash_password_unicode_characters(self, password_hasher):
        """Test hashing password with unicode characters."""
        password = "pässwörd123🔐"

        hashed = password_hasher.hash_password(password)

        assert isinstance(hashed, str)
        assert bcrypt.checkpw(password.encode("utf-8"), hashed.encode("utf-8"))

    def test_hash_password_very_long_password(self, password_hasher):
        """Test hashing very long password."""
        password = "a" * 1000  # 1000 character password

        hashed = password_hasher.hash_password(password)

        assert isinstance(hashed, str)
        assert bcrypt.checkpw(password.encode("utf-8"), hashed.encode("utf-8"))

    def test_hash_password_special_characters(self, password_hasher):
        """Test hashing password with special characters."""
        password = "p@ssw0rd!@#$%^&*()_+-=[]{}|;':\"<>?,./"

        hashed = password_hasher.hash_password(password)

        assert isinstance(hashed, str)
        assert bcrypt.checkpw(password.encode("utf-8"), hashed.encode("utf-8"))

    def test_hash_password_different_rounds(self, mock_settings):
        """Test hashing with different bcrypt rounds."""
        # Test with different round values
        for rounds in [4, 8, 12, 14]:
            mock_settings.security.PASSWORD_HASH_ROUNDS = rounds
            hasher = PasswordHasher(settings=mock_settings)

            password = "testpassword123"
            hashed = hasher.hash_password(password)

            # Verify the hash uses the correct number of rounds
            assert hashed.startswith(f"$2b${rounds:02d}$")
            assert bcrypt.checkpw(password.encode("utf-8"), hashed.encode("utf-8"))

    def test_hash_password_salt_uniqueness(self, password_hasher):
        """Test that same password produces different hashes (due to salt)."""
        password = "samepassword123"

        hash1 = password_hasher.hash_password(password)
        hash2 = password_hasher.hash_password(password)

        # Hashes should be different due to different salts
        assert hash1 != hash2

        # But both should verify correctly
        assert bcrypt.checkpw(password.encode("utf-8"), hash1.encode("utf-8"))
        assert bcrypt.checkpw(password.encode("utf-8"), hash2.encode("utf-8"))

    def test_hash_password_bcrypt_exception_handling(self, password_hasher):
        """Test handling of bcrypt exceptions during hashing."""
        password = "validpassword123"

        with patch("bcrypt.gensalt", side_effect=Exception("bcrypt error")):
            with pytest.raises(
                ValueError, match="Could not securely hash the password"
            ):
                password_hasher.hash_password(password)

    def test_hash_password_encoding_exception_handling(self, password_hasher):
        """Test handling of encoding exceptions during hashing."""
        # Mock string encode method to raise exception
        with patch.object(
            str,
            "encode",
            side_effect=UnicodeEncodeError("utf-8", "", 0, 1, "test error"),
        ):
            with pytest.raises(
                ValueError, match="Could not securely hash the password"
            ):
                password_hasher.hash_password("validpassword123")

    def test_verify_password_correct_password(self, password_hasher):
        """Test verifying correct password against hash."""
        password = "correctpassword123"
        hashed = password_hasher.hash_password(password)

        result = password_hasher.verify_password(password, hashed)

        assert result is True

    def test_verify_password_incorrect_password(self, password_hasher):
        """Test verifying incorrect password against hash."""
        password = "correctpassword123"
        wrong_password = "wrongpassword123"
        hashed = password_hasher.hash_password(password)

        result = password_hasher.verify_password(wrong_password, hashed)

        assert result is False

    def test_verify_password_empty_password(self, password_hasher):
        """Test verifying empty password."""
        password = "correctpassword123"
        hashed = password_hasher.hash_password(password)

        result = password_hasher.verify_password("", hashed)

        assert result is False

    def test_verify_password_none_password(self, password_hasher):
        """Test verifying None password."""
        password = "correctpassword123"
        hashed = password_hasher.hash_password(password)

        result = password_hasher.verify_password(None, hashed)

        assert result is False

    def test_verify_password_empty_hash(self, password_hasher):
        """Test verifying against empty hash."""
        password = "correctpassword123"

        result = password_hasher.verify_password(password, "")

        assert result is False

    def test_verify_password_none_hash(self, password_hasher):
        """Test verifying against None hash."""
        password = "correctpassword123"

        result = password_hasher.verify_password(password, None)

        assert result is False

    def test_verify_password_malformed_hash(self, password_hasher):
        """Test verifying against malformed hash."""
        password = "correctpassword123"
        malformed_hash = "not_a_valid_bcrypt_hash"

        # Should perform dummy hash operation for timing attack mitigation
        with patch.object(password_hasher, "hash_password") as mock_hash:
            result = password_hasher.verify_password(password, malformed_hash)

            assert result is False
            # Verify dummy hash operation was called
            mock_hash.assert_called_once_with("a" * password_hasher.password_min_length)

    def test_verify_password_invalid_hash_format(self, password_hasher):
        """Test verifying against various invalid hash formats."""
        password = "correctpassword123"
        invalid_hashes = [
            "plaintext",
            "$2b$invalid",
            "$2b$12$tooshort",
            "$2a$12$" + "x" * 50,  # Wrong bcrypt version
            "random_string_123",
            "{'hash': 'fake'}",
            "null",
            "undefined",
        ]

        for invalid_hash in invalid_hashes:
            with patch.object(password_hasher, "hash_password") as mock_hash:
                result = password_hasher.verify_password(password, invalid_hash)

                assert result is False
                # Verify dummy hash operation was called for timing attack
                # mitigation
                mock_hash.assert_called_once_with(
                    "a" * password_hasher.password_min_length
                )
                mock_hash.reset_mock()

    def test_verify_password_unicode_characters(self, password_hasher):
        """Test verifying password with unicode characters."""
        password = "pässwörd123🔐"
        hashed = password_hasher.hash_password(password)

        result = password_hasher.verify_password(password, hashed)

        assert result is True

    def test_verify_password_case_sensitivity(self, password_hasher):
        """Test that password verification is case sensitive."""
        password = "CaseSensitive123"
        wrong_case = "casesensitive123"
        hashed = password_hasher.hash_password(password)

        correct_result = password_hasher.verify_password(password, hashed)
        wrong_result = password_hasher.verify_password(wrong_case, hashed)

        assert correct_result is True
        assert wrong_result is False

    def test_verify_password_whitespace_sensitivity(self, password_hasher):
        """Test that password verification is sensitive to whitespace."""
        password = "password123"
        password_with_space = "password123 "
        hashed = password_hasher.hash_password(password)

        correct_result = password_hasher.verify_password(password, hashed)
        wrong_result = password_hasher.verify_password(password_with_space, hashed)

        assert correct_result is True
        assert wrong_result is False

    def test_verify_password_timing_attack_resistance(self, password_hasher):
        """Test timing attack resistance by measuring verification times."""
        password = "correctpassword123"
        hashed = password_hasher.hash_password(password)

        # Measure time for correct password
        start_time = time.time()
        password_hasher.verify_password(password, hashed)
        correct_time = time.time() - start_time

        # Measure time for incorrect password
        start_time = time.time()
        password_hasher.verify_password("wrongpassword123", hashed)
        incorrect_time = time.time() - start_time

        # Measure time for malformed hash (triggers dummy hash operation)
        start_time = time.time()
        password_hasher.verify_password(password, "malformed_hash")
        malformed_time = time.time() - start_time

        # Times should be relatively similar (within reasonable bounds)
        # bcrypt verification is designed to be slow and consistent
        assert correct_time > 0.001  # Should take some time due to bcrypt
        assert incorrect_time > 0.001
        assert malformed_time > 0.001  # Should take time due to dummy hash

        # Timing difference should not be extreme (within factor of 10)
        time_ratio = max(correct_time, incorrect_time) / min(
            correct_time, incorrect_time
        )
        assert time_ratio < 10  # Reasonable bound for timing consistency

    def test_verify_password_bcrypt_exception_handling(self, password_hasher):
        """Test handling of bcrypt exceptions during verification."""
        password = "correctpassword123"
        valid_hash = password_hasher.hash_password(password)

        with patch("bcrypt.checkpw", side_effect=ValueError("bcrypt error")):
            with patch.object(password_hasher, "hash_password") as mock_hash:
                result = password_hasher.verify_password(password, valid_hash)

                assert result is False
                # Should perform dummy hash operation
                mock_hash.assert_called_once_with(
                    "a" * password_hasher.password_min_length
                )

    def test_verify_password_encoding_exception_handling(self, password_hasher):
        """Test handling of encoding exceptions during verification."""
        password = "correctpassword123"
        valid_hash = password_hasher.hash_password(password)

        with patch.object(
            str,
            "encode",
            side_effect=UnicodeEncodeError("utf-8", "", 0, 1, "test error"),
        ):
            with patch.object(password_hasher, "hash_password") as mock_hash:
                result = password_hasher.verify_password(password, valid_hash)

                assert result is False
                # Should perform dummy hash operation
                mock_hash.assert_called_once_with(
                    "a" * password_hasher.password_min_length
                )

    def test_concurrent_password_operations(self, password_hasher):
        """Test concurrent password hashing and verification operations."""
        password = "concurrentpassword123"
        results = []
        errors = []

        def hash_and_verify():
            try:
                hashed = password_hasher.hash_password(password)
                verified = password_hasher.verify_password(password, hashed)
                results.append((hashed, verified))
            except Exception as e:
                errors.append(e)

        # Create multiple threads for concurrent operations
        threads = []
        for _ in range(10):
            thread = threading.Thread(target=hash_and_verify)
            threads.append(thread)

        # Start all threads
        for thread in threads:
            thread.start()

        # Wait for completion
        for thread in threads:
            thread.join()

        # Verify results
        assert len(errors) == 0  # No errors should occur
        assert len(results) == 10  # All operations should complete

        # All verifications should succeed
        for hashed, verified in results:
            assert isinstance(hashed, str)
            assert verified is True

        # All hashes should be unique (due to salt)
        hashes = [result[0] for result in results]
        assert len(set(hashes)) == len(hashes)

    def test_password_complexity_scenarios(self, password_hasher):
        """Test various password complexity scenarios."""
        test_passwords = [
            "simple123",
            "Complex123!",
            "VeryLongPasswordWithManyCharacters123456789",
            "WithNumbers123AndSymbols!@#",
            "MixedCASE123lower",
            "OnlyNumbers123456789",
            "OnlyLettersNoNumbers",
            "Sp3c!@lCh@r@ct3r$",
            "   spaces   everywhere   ",
            "tabsandnewlines\t\n",
            "unicode🔐password💪",
            "CombinationOfEverything123!@#🔐",
        ]

        for password in test_passwords:
            if len(password) >= password_hasher.password_min_length:
                hashed = password_hasher.hash_password(password)
                verified = password_hasher.verify_password(password, hashed)

                assert isinstance(hashed, str)
                assert verified is True

                # Verify wrong password fails
                wrong_verified = password_hasher.verify_password(
                    password + "wrong", hashed
                )
                assert wrong_verified is False

    def test_hash_password_performance_characteristics(self, password_hasher):
        """Test that password hashing has appropriate performance characteristics."""
        password = "performancetest123"

        # Measure hashing time
        start_time = time.time()
        hashed = password_hasher.hash_password(password)
        hash_time = time.time() - start_time

        # Measure verification time
        start_time = time.time()
        verified = password_hasher.verify_password(password, hashed)
        verify_time = time.time() - start_time

        # bcrypt should be slow enough to prevent brute force attacks
        assert hash_time > 0.01  # Should take at least 10ms
        assert verify_time > 0.01  # Should take at least 10ms
        assert verified is True

        # But not so slow as to be unusable
        assert hash_time < 10.0  # Should complete within 10 seconds
        assert verify_time < 10.0  # Should complete within 10 seconds

    def test_bcrypt_rounds_security_levels(self, mock_settings):
        """Test different bcrypt rounds provide appropriate security levels."""
        password = "securitytest123"

        # Test with different security levels
        rounds_tests = [
            (4, "fast"),  # Fast but less secure
            (8, "balanced"),  # Balanced
            (12, "secure"),  # Secure
            (14, "high"),  # High security
        ]

        for rounds, level in rounds_tests:
            mock_settings.security.PASSWORD_HASH_ROUNDS = rounds
            hasher = PasswordHasher(settings=mock_settings)

            start_time = time.time()
            hashed = hasher.hash_password(password)
            hash_time = time.time() - start_time

            # Verify hash format
            assert hashed.startswith(f"$2b${rounds:02d}$")

            # Verify functionality
            assert hasher.verify_password(password, hashed) is True
            assert hasher.verify_password("wrong", hashed) is False

            # Higher rounds should generally take longer (though timing can
            # vary)
            if rounds >= 12:
                assert hash_time > 0.01  # Should be slow enough for security

    def test_password_hasher_logging_behavior(self, password_hasher):
        """Test that password hasher logs appropriate messages."""
        with patch("src.infrastructure.security.password_hasher.logger") as mock_logger:
            # Test successful operations (should not log errors)
            password = "loggingtest123"
            hashed = password_hasher.hash_password(password)
            verified = password_hasher.verify_password(password, hashed)

            assert verified is True
            # Should not log any errors for successful operations
            mock_logger.error.assert_not_called()
            mock_logger.critical.assert_not_called()

            # Test malformed hash (should log warning)
            password_hasher.verify_password(password, "malformed_hash")
            mock_logger.warning.assert_called()

            # Test hashing exception (should log critical)
            with patch("bcrypt.gensalt", side_effect=Exception("test error")):
                with pytest.raises(ValueError):
                    password_hasher.hash_password(password)
                mock_logger.critical.assert_called()

    def test_password_hasher_memory_usage(self, password_hasher):
        """Test that password hasher doesn't leak memory during operations."""
        import gc

        # Perform many operations to check for memory leaks
        password = "memorytest123"

        # Get baseline memory usage
        gc.collect()
        initial_objects = len(gc.get_objects())

        # Perform many hash/verify operations
        for _ in range(100):
            hashed = password_hasher.hash_password(password)
            verified = password_hasher.verify_password(password, hashed)
            assert verified is True

        # Check final memory usage
        gc.collect()
        final_objects = len(gc.get_objects())

        # Object count should not grow significantly (allow some variance)
        object_increase = final_objects - initial_objects
        assert object_increase < 1000  # Reasonable bound for object growth

    def test_password_hasher_deterministic_behavior(self, password_hasher):
        """Test that password hasher behaves deterministically for verification."""
        password = "deterministictest123"
        hashed = password_hasher.hash_password(password)

        # Verify multiple times - should always return the same result
        for _ in range(10):
            result = password_hasher.verify_password(password, hashed)
            assert result is True

            wrong_result = password_hasher.verify_password("wrong", hashed)
            assert wrong_result is False

    def test_password_hasher_cross_instance_compatibility(self, mock_settings):
        """Test that hashes from one instance can be verified by another."""
        password = "crossinstancetest123"

        # Create first hasher instance
        hasher1 = PasswordHasher(settings=mock_settings)
        hashed = hasher1.hash_password(password)

        # Create second hasher instance with same settings
        hasher2 = PasswordHasher(settings=mock_settings)
        verified = hasher2.verify_password(password, hashed)

        assert verified is True
        assert hasher2.verify_password("wrong", hashed) is False

    def test_password_hasher_settings_changes(self, mock_settings):
        """Test password hasher behavior when settings change."""
        password = "settingschangetest123"

        # Create hasher with initial settings
        mock_settings.security.PASSWORD_HASH_ROUNDS = 8
        hasher = PasswordHasher(settings=mock_settings)
        hashed = hasher.hash_password(password)

        # Change settings (should not affect verification of existing hashes)
        mock_settings.security.PASSWORD_HASH_ROUNDS = 12
        new_hasher = PasswordHasher(settings=mock_settings)

        # Should still verify old hash correctly
        verified = new_hasher.verify_password(password, hashed)
        assert verified is True

        # New hashes should use new settings
        new_hashed = new_hasher.hash_password(password)
        assert new_hashed.startswith("$2b$12$")  # New rounds
        assert hashed.startswith("$2b$08$")  # Old rounds

    def test_password_hasher_edge_case_inputs(self, password_hasher):
        """Test password hasher with edge case inputs."""
        # Test with minimum length passwords
        min_password = "a" * password_hasher.password_min_length
        hashed = password_hasher.hash_password(min_password)
        assert password_hasher.verify_password(min_password, hashed) is True

        # Test with very long passwords
        long_password = "a" * 10000
        hashed = password_hasher.hash_password(long_password)
        assert password_hasher.verify_password(long_password, hashed) is True

        # Test with passwords containing null bytes (should work)
        null_password = "password\x00with\x00nulls"
        if len(null_password) >= password_hasher.password_min_length:
            hashed = password_hasher.hash_password(null_password)
            assert password_hasher.verify_password(null_password, hashed) is True

    def test_password_hasher_error_message_security(self, password_hasher):
        """Test that error messages don't leak sensitive information."""
        # Test with short password
        with pytest.raises(ValueError) as exc_info:
            password_hasher.hash_password("short")

        error_message = str(exc_info.value)
        assert "short" not in error_message  # Should not echo the password
        assert "security requirements" in error_message

        # Test with bcrypt exception
        with patch("bcrypt.gensalt", side_effect=Exception("internal bcrypt error")):
            with pytest.raises(ValueError) as exc_info:
                password_hasher.hash_password("validpassword123")

            error_message = str(exc_info.value)
            assert (
                "internal bcrypt error" not in error_message
            )  # Should not expose internal error
            assert "Could not securely hash" in error_message
