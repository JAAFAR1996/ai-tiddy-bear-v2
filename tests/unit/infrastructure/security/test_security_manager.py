"""Tests for Security Manager
Testing core security functions for passwords, tokens, and cryptographic operations.
"""

import hashlib
import threading
import time
from unittest.mock import Mock, patch

from src.infrastructure.security.child_safety.security_manager import (
    CoreSecurityManager as SecurityManager,
)
from src.infrastructure.security.child_safety.security_manager import security_manager


class TestSecurityManager:
    """Test the Security Manager class."""

    def test_hash_password_basic(self):
        """Test basic password hashing functionality."""
        password = "test_password_123"

        hashed = SecurityManager.hash_password(password)

        assert isinstance(hashed, str)
        assert len(hashed) > 0
        assert hashed != password  # Should not be plaintext
        assert hashed.startswith("$2b$")  # bcrypt hash format

    def test_hash_password_different_passwords_different_hashes(self):
        """Test that different passwords produce different hashes."""
        password1 = "password1"
        password2 = "password2"

        hash1 = SecurityManager.hash_password(password1)
        hash2 = SecurityManager.hash_password(password2)

        assert hash1 != hash2

    def test_hash_password_same_password_different_salts(self):
        """Test that same password produces different hashes due to salts."""
        password = "same_password"

        hash1 = SecurityManager.hash_password(password)
        hash2 = SecurityManager.hash_password(password)

        # Should be different due to random salt
        assert hash1 != hash2

        # But both should verify correctly
        assert SecurityManager.verify_password(password, hash1)
        assert SecurityManager.verify_password(password, hash2)

    def test_hash_password_empty_string(self):
        """Test hashing empty string."""
        password = ""

        hashed = SecurityManager.hash_password(password)

        assert isinstance(hashed, str)
        assert len(hashed) > 0
        assert SecurityManager.verify_password(password, hashed)

    def test_hash_password_unicode_characters(self):
        """Test hashing password with unicode characters."""
        password = "pässwörd_测试_🔐"

        hashed = SecurityManager.hash_password(password)

        assert isinstance(hashed, str)
        assert SecurityManager.verify_password(password, hashed)

    def test_hash_password_very_long_password(self):
        """Test hashing very long password."""
        password = "a" * 1000  # 1000 character password

        hashed = SecurityManager.hash_password(password)

        assert isinstance(hashed, str)
        assert SecurityManager.verify_password(password, hashed)

    def test_hash_password_special_characters(self):
        """Test hashing password with special characters."""
        password = "p@ssw0rd!@#$%^&*()_+-=[]{}|;':\"<>?,./"

        hashed = SecurityManager.hash_password(password)

        assert isinstance(hashed, str)
        assert SecurityManager.verify_password(password, hashed)

    def test_hash_password_whitespace_characters(self):
        """Test hashing password with whitespace characters."""
        password = "  password with spaces  \t\n"

        hashed = SecurityManager.hash_password(password)

        assert isinstance(hashed, str)
        assert SecurityManager.verify_password(password, hashed)

    def test_hash_password_bcrypt_parameters(self):
        """Test that bcrypt is called with correct parameters."""
        password = "test_password"

        with patch("bcrypt.gensalt") as mock_gensalt:
            with patch("bcrypt.hashpw") as mock_hashpw:
                mock_gensalt.return_value = b"fake_salt"
                mock_hashpw.return_value = b"fake_hash"

                SecurityManager.hash_password(password)

                mock_gensalt.assert_called_once()
                mock_hashpw.assert_called_once_with(
                    password.encode("utf-8"), b"fake_salt"
                )

    def test_hash_password_encoding_handling(self):
        """Test password encoding is handled correctly."""
        password = "test_password"

        with patch("bcrypt.hashpw") as mock_hashpw:
            mock_hashpw.return_value = b"fake_hash"

            SecurityManager.hash_password(password)

            # Should encode password as utf-8
            call_args = mock_hashpw.call_args[0]
            assert call_args[0] == password.encode("utf-8")

    def test_verify_password_correct_password(self):
        """Test verifying correct password."""
        password = "correct_password"
        hashed = SecurityManager.hash_password(password)

        result = SecurityManager.verify_password(password, hashed)

        assert result is True

    def test_verify_password_incorrect_password(self):
        """Test verifying incorrect password."""
        correct_password = "correct_password"
        wrong_password = "wrong_password"
        hashed = SecurityManager.hash_password(correct_password)

        result = SecurityManager.verify_password(wrong_password, hashed)

        assert result is False

    def test_verify_password_empty_passwords(self):
        """Test verifying empty passwords."""
        empty_password = ""
        hashed = SecurityManager.hash_password(empty_password)

        # Correct empty password
        assert SecurityManager.verify_password(empty_password, hashed) is True

        # Wrong password against empty hash
        assert SecurityManager.verify_password("not_empty", hashed) is False

    def test_verify_password_case_sensitivity(self):
        """Test password verification is case sensitive."""
        password = "CaseSensitive"
        wrong_case = "casesensitive"
        hashed = SecurityManager.hash_password(password)

        assert SecurityManager.verify_password(password, hashed) is True
        assert SecurityManager.verify_password(wrong_case, hashed) is False

    def test_verify_password_unicode_characters(self):
        """Test verifying password with unicode characters."""
        password = "pässwörd_测试_🔐"
        hashed = SecurityManager.hash_password(password)

        assert SecurityManager.verify_password(password, hashed) is True
        assert SecurityManager.verify_password("different_unicode", hashed) is False

    def test_verify_password_invalid_hash(self):
        """Test verifying password with invalid hash."""
        password = "test_password"
        invalid_hash = "not_a_bcrypt_hash"

        result = SecurityManager.verify_password(password, invalid_hash)

        assert result is False

    def test_verify_password_empty_hash(self):
        """Test verifying password with empty hash."""
        password = "test_password"

        result = SecurityManager.verify_password(password, "")

        assert result is False

    def test_verify_password_bcrypt_parameters(self):
        """Test that bcrypt.checkpw is called with correct parameters."""
        password = "test_password"
        hashed = "fake_hash"

        with patch("bcrypt.checkpw") as mock_checkpw:
            mock_checkpw.return_value = True

            SecurityManager.verify_password(password, hashed)

            mock_checkpw.assert_called_once_with(
                password.encode("utf-8"), hashed.encode("utf-8")
            )

    def test_verify_password_encoding_handling(self):
        """Test password and hash encoding is handled correctly."""
        password = "test_password"
        hashed = "fake_hash"

        with patch("bcrypt.checkpw") as mock_checkpw:
            mock_checkpw.return_value = True

            SecurityManager.verify_password(password, hashed)

            call_args = mock_checkpw.call_args[0]
            assert call_args[0] == password.encode("utf-8")
            assert call_args[1] == hashed.encode("utf-8")

    def test_generate_secure_token_default_length(self):
        """Test generating secure token with default length."""
        token = SecurityManager.generate_secure_token()

        assert isinstance(token, str)
        assert len(token) == 64  # 32 bytes = 64 hex characters
        assert all(c in "0123456789abcdef" for c in token)

    def test_generate_secure_token_custom_length(self):
        """Test generating secure token with custom length."""
        lengths = [8, 16, 32, 64, 128]

        for length in lengths:
            token = SecurityManager.generate_secure_token(length)

            assert isinstance(token, str)
            assert len(token) == length * 2  # hex encoding doubles length
            assert all(c in "0123456789abcdef" for c in token)

    def test_generate_secure_token_zero_length(self):
        """Test generating secure token with zero length."""
        token = SecurityManager.generate_secure_token(0)

        assert isinstance(token, str)
        assert len(token) == 0

    def test_generate_secure_token_uniqueness(self):
        """Test that generated tokens are unique."""
        tokens = [SecurityManager.generate_secure_token() for _ in range(100)]

        # All tokens should be unique
        assert len(set(tokens)) == len(tokens)

    def test_generate_secure_token_randomness(self):
        """Test that generated tokens have good randomness."""
        tokens = [SecurityManager.generate_secure_token(32) for _ in range(100)]

        # Test character distribution
        all_chars = "".join(tokens)
        char_counts = {c: all_chars.count(c) for c in "0123456789abcdef"}

        # Characters should be reasonably distributed
        min_count = min(char_counts.values())
        max_count = max(char_counts.values())

        # Allow some variation but not extreme skew
        assert max_count / min_count < 2.0

    def test_generate_secure_token_secrets_usage(self):
        """Test that secrets.token_hex is used correctly."""
        length = 16

        with patch("secrets.token_hex") as mock_token_hex:
            mock_token_hex.return_value = "fake_token"

            result = SecurityManager.generate_secure_token(length)

            mock_token_hex.assert_called_once_with(length)
            assert result == "fake_token"

    def test_secure_compare_identical_strings(self):
        """Test secure comparison of identical strings."""
        string1 = "identical_string"
        string2 = "identical_string"

        result = SecurityManager.secure_compare(string1, string2)

        assert result is True

    def test_secure_compare_different_strings(self):
        """Test secure comparison of different strings."""
        string1 = "string1"
        string2 = "string2"

        result = SecurityManager.secure_compare(string1, string2)

        assert result is False

    def test_secure_compare_identical_bytes(self):
        """Test secure comparison of identical bytes."""
        bytes1 = b"identical_bytes"
        bytes2 = b"identical_bytes"

        result = SecurityManager.secure_compare(bytes1, bytes2)

        assert result is True

    def test_secure_compare_different_bytes(self):
        """Test secure comparison of different bytes."""
        bytes1 = b"bytes1"
        bytes2 = b"bytes2"

        result = SecurityManager.secure_compare(bytes1, bytes2)

        assert result is False

    def test_secure_compare_mixed_types(self):
        """Test secure comparison of mixed string and bytes types."""
        string_val = "test_value"
        bytes_val = b"test_value"

        result = SecurityManager.secure_compare(string_val, bytes_val)

        assert result is True

    def test_secure_compare_empty_values(self):
        """Test secure comparison of empty values."""
        assert SecurityManager.secure_compare("", "") is True
        assert SecurityManager.secure_compare(b"", b"") is True
        assert SecurityManager.secure_compare("", b"") is True
        assert SecurityManager.secure_compare("", "non_empty") is False
        assert SecurityManager.secure_compare(b"", b"non_empty") is False

    def test_secure_compare_unicode_strings(self):
        """Test secure comparison of unicode strings."""
        unicode1 = "tëst_ünïcödé_🔐"
        unicode2 = "tëst_ünïcödé_🔐"
        unicode3 = "different_ünïcödé_🔒"

        assert SecurityManager.secure_compare(unicode1, unicode2) is True
        assert SecurityManager.secure_compare(unicode1, unicode3) is False

    def test_secure_compare_case_sensitivity(self):
        """Test secure comparison is case sensitive."""
        string1 = "CaseSensitive"
        string2 = "casesensitive"

        result = SecurityManager.secure_compare(string1, string2)

        assert result is False

    def test_secure_compare_whitespace_sensitivity(self):
        """Test secure comparison is whitespace sensitive."""
        string1 = "test"
        string2 = "test "

        result = SecurityManager.secure_compare(string1, string2)

        assert result is False

    def test_secure_compare_hmac_usage(self):
        """Test that hmac.compare_digest is used correctly."""
        val1 = "test1"
        val2 = "test2"

        with patch("hmac.compare_digest") as mock_compare:
            mock_compare.return_value = True

            result = SecurityManager.secure_compare(val1, val2)

            mock_compare.assert_called_once_with(val1, val2)
            assert result is True

    def test_secure_compare_timing_resistance(self):
        """Test secure comparison timing resistance."""
        # This test ensures the function takes similar time regardless of where
        # strings differ
        string1 = "a" * 1000
        string2 = "b" + "a" * 999  # Different at start
        string3 = "a" * 999 + "b"  # Different at end

        # Multiple timing measurements
        times = []
        for strings in [(string1, string2), (string1, string3)]:
            start_time = time.time()
            for _ in range(100):
                SecurityManager.secure_compare(strings[0], strings[1])
            end_time = time.time()
            times.append(end_time - start_time)

        # Times should be similar (within reasonable variation)
        if len(times) > 1:
            ratio = max(times) / min(times)
            assert ratio < 2.0  # Allow some variation but not extreme differences

    def test_generate_file_signature_basic(self):
        """Test basic file signature generation."""
        file_content = b"test file content"
        secret_key = "secret_key"

        signature = SecurityManager.generate_file_signature(file_content, secret_key)

        assert isinstance(signature, str)
        assert len(signature) == 64  # SHA256 hex = 64 characters
        assert all(c in "0123456789abcdef" for c in signature)

    def test_generate_file_signature_different_content(self):
        """Test file signature with different content produces different signatures."""
        content1 = b"file content 1"
        content2 = b"file content 2"
        secret_key = "secret_key"

        signature1 = SecurityManager.generate_file_signature(content1, secret_key)
        signature2 = SecurityManager.generate_file_signature(content2, secret_key)

        assert signature1 != signature2

    def test_generate_file_signature_different_keys(self):
        """Test file signature with different keys produces different signatures."""
        file_content = b"same file content"
        key1 = "secret_key_1"
        key2 = "secret_key_2"

        signature1 = SecurityManager.generate_file_signature(file_content, key1)
        signature2 = SecurityManager.generate_file_signature(file_content, key2)

        assert signature1 != signature2

    def test_generate_file_signature_empty_content(self):
        """Test file signature with empty content."""
        file_content = b""
        secret_key = "secret_key"

        signature = SecurityManager.generate_file_signature(file_content, secret_key)

        assert isinstance(signature, str)
        assert len(signature) == 64

    def test_generate_file_signature_empty_key(self):
        """Test file signature with empty key."""
        file_content = b"test content"
        secret_key = ""

        signature = SecurityManager.generate_file_signature(file_content, secret_key)

        assert isinstance(signature, str)
        assert len(signature) == 64

    def test_generate_file_signature_large_content(self):
        """Test file signature with large content."""
        file_content = b"x" * 1000000  # 1MB of data
        secret_key = "secret_key"

        signature = SecurityManager.generate_file_signature(file_content, secret_key)

        assert isinstance(signature, str)
        assert len(signature) == 64

    def test_generate_file_signature_binary_content(self):
        """Test file signature with binary content."""
        file_content = bytes(range(256))  # All possible byte values
        secret_key = "secret_key"

        signature = SecurityManager.generate_file_signature(file_content, secret_key)

        assert isinstance(signature, str)
        assert len(signature) == 64

    def test_generate_file_signature_unicode_key(self):
        """Test file signature with unicode key."""
        file_content = b"test content"
        secret_key = "sëcrét_këy_🔐"

        signature = SecurityManager.generate_file_signature(file_content, secret_key)

        assert isinstance(signature, str)
        assert len(signature) == 64

    def test_generate_file_signature_consistency(self):
        """Test file signature consistency (same inputs produce same output)."""
        file_content = b"consistent test content"
        secret_key = "consistent_key"

        signature1 = SecurityManager.generate_file_signature(file_content, secret_key)
        signature2 = SecurityManager.generate_file_signature(file_content, secret_key)

        assert signature1 == signature2

    def test_generate_file_signature_hmac_usage(self):
        """Test that HMAC is used correctly for file signatures."""
        file_content = b"test content"
        secret_key = "secret_key"

        with patch("hmac.new") as mock_hmac:
            mock_hmac_instance = Mock()
            mock_hmac_instance.hexdigest.return_value = "fake_signature"
            mock_hmac.return_value = mock_hmac_instance

            result = SecurityManager.generate_file_signature(file_content, secret_key)

            mock_hmac.assert_called_once_with(
                secret_key.encode("utf-8"), file_content, hashlib.sha256
            )
            assert result == "fake_signature"

    def test_generate_file_signature_key_encoding(self):
        """Test that secret key is properly encoded for HMAC."""
        file_content = b"test content"
        secret_key = "test_key"

        with patch("hmac.new") as mock_hmac:
            mock_hmac_instance = Mock()
            mock_hmac_instance.hexdigest.return_value = "fake_signature"
            mock_hmac.return_value = mock_hmac_instance

            SecurityManager.generate_file_signature(file_content, secret_key)

            call_args = mock_hmac.call_args[0]
            assert call_args[0] == secret_key.encode("utf-8")
            assert call_args[1] == file_content
            assert call_args[2] == hashlib.sha256

    def test_generate_file_signature_verification(self):
        """Test file signature can be used for verification."""
        file_content = b"original file content"
        modified_content = b"modified file content"
        secret_key = "verification_key"

        original_signature = SecurityManager.generate_file_signature(
            file_content, secret_key
        )
        verification_signature = SecurityManager.generate_file_signature(
            file_content, secret_key
        )
        modified_signature = SecurityManager.generate_file_signature(
            modified_content, secret_key
        )

        # Same content should produce same signature
        assert original_signature == verification_signature

        # Different content should produce different signature
        assert original_signature != modified_signature

        # Can use secure_compare for verification
        assert SecurityManager.secure_compare(
            original_signature, verification_signature
        )
        assert not SecurityManager.secure_compare(
            original_signature, modified_signature
        )


class TestSecurityManagerIntegration:
    """Integration tests for SecurityManager."""

    def test_password_hash_verify_integration(self):
        """Test password hashing and verification integration."""
        passwords = [
            "simple_password",
            "complex_pässwörd_123!@#",
            "very_long_password" * 10,
            "",
            "unicode_🔐_password",
            "   spaces   ",
            "newlines\nand\ttabs",
        ]

        for password in passwords:
            hashed = SecurityManager.hash_password(password)

            # Correct password should verify
            assert SecurityManager.verify_password(password, hashed)

            # Wrong password should not verify
            assert not SecurityManager.verify_password(password + "wrong", hashed)

    def test_token_generation_security_properties(self):
        """Test token generation security properties."""
        # Generate many tokens to test randomness
        tokens = [SecurityManager.generate_secure_token() for _ in range(1000)]

        # All tokens should be unique
        assert len(set(tokens)) == len(tokens)

        # Tokens should have good length distribution
        lengths = [len(token) for token in tokens]
        # All should be 64 chars
        assert all(length == 64 for length in lengths)

        # Tokens should use valid hex characters
        for token in tokens:
            assert all(c in "0123456789abcdef" for c in token)

    def test_secure_compare_integration(self):
        """Test secure comparison integration with other functions."""
        # Test with password hashes
        password = "test_password"
        hash1 = SecurityManager.hash_password(password)
        hash2 = SecurityManager.hash_password(password)

        # Different hashes of same password should not be equal
        assert not SecurityManager.secure_compare(hash1, hash2)

        # Test with tokens
        token1 = SecurityManager.generate_secure_token()
        token2 = SecurityManager.generate_secure_token()

        # Different tokens should not be equal
        assert not SecurityManager.secure_compare(token1, token2)

        # Same token should be equal
        assert SecurityManager.secure_compare(token1, token1)

    def test_file_signature_integration(self):
        """Test file signature integration and verification workflow."""
        # Simulate file integrity checking workflow
        original_content = b"Important file content that must not be tampered with"
        secret_key = SecurityManager.generate_secure_token()

        # Generate signature for original content
        original_signature = SecurityManager.generate_file_signature(
            original_content, secret_key
        )

        # Verify signature matches
        verification_signature = SecurityManager.generate_file_signature(
            original_content, secret_key
        )
        assert SecurityManager.secure_compare(
            original_signature, verification_signature
        )

        # Detect tampering
        tampered_content = b"Important file content that HAS BEEN tampered with"
        tampered_signature = SecurityManager.generate_file_signature(
            tampered_content, secret_key
        )
        assert not SecurityManager.secure_compare(
            original_signature, tampered_signature
        )

    def test_concurrent_operations(self):
        """Test concurrent operations are thread-safe."""
        results = []
        errors = []

        def worker():
            try:
                # Test all main operations
                password = "concurrent_test"
                hashed = SecurityManager.hash_password(password)
                verified = SecurityManager.verify_password(password, hashed)
                token = SecurityManager.generate_secure_token()
                compared = SecurityManager.secure_compare(token, token)
                signature = SecurityManager.generate_file_signature(b"test", "key")

                results.append((verified, compared, len(token), len(signature)))
            except Exception as e:
                errors.append(e)

        # Create multiple threads
        threads = []
        for _ in range(10):
            thread = threading.Thread(target=worker)
            threads.append(thread)

        # Start all threads
        for thread in threads:
            thread.start()

        # Wait for completion
        for thread in threads:
            thread.join()

        # Verify results
        assert len(errors) == 0
        assert len(results) == 10

        for verified, compared, token_len, signature_len in results:
            assert verified is True
            assert compared is True
            assert token_len == 64
            assert signature_len == 64

    def test_cross_function_compatibility(self):
        """Test compatibility between different security functions."""
        # Generate secure key for file signatures
        secret_key = SecurityManager.generate_secure_token()

        # Hash a password
        password = "cross_function_test"
        hashed_password = SecurityManager.hash_password(password)

        # Use hashed password as file content
        file_content = hashed_password.encode("utf-8")
        signature = SecurityManager.generate_file_signature(file_content, secret_key)

        # Verify all components work together
        assert SecurityManager.verify_password(password, hashed_password)
        assert SecurityManager.secure_compare(signature, signature)

        # Generate new signature with same content
        new_signature = SecurityManager.generate_file_signature(
            file_content, secret_key
        )
        assert SecurityManager.secure_compare(signature, new_signature)

    def test_performance_characteristics(self):
        """Test performance characteristics of security functions."""
        import time

        # Test password hashing performance
        password = "performance_test"
        start_time = time.time()
        for _ in range(10):
            SecurityManager.hash_password(password)
        hash_time = time.time() - start_time

        # Should be slow enough for security but not too slow
        assert hash_time > 0.01  # At least 1ms per hash
        assert hash_time < 10.0  # Less than 10 seconds for 10 hashes

        # Test token generation performance
        start_time = time.time()
        for _ in range(1000):
            SecurityManager.generate_secure_token()
        token_time = time.time() - start_time

        # Should be fast
        assert token_time < 1.0  # Less than 1 second for 1000 tokens

        # Test file signature performance
        file_content = b"x" * 10000  # 10KB file
        secret_key = "performance_key"
        start_time = time.time()
        for _ in range(100):
            SecurityManager.generate_file_signature(file_content, secret_key)
        signature_time = time.time() - start_time

        # Should be reasonably fast
        assert signature_time < 1.0  # Less than 1 second for 100 signatures

    def test_memory_safety(self):
        """Test memory safety with large inputs."""
        # Test with large password
        large_password = "p" * 100000
        hashed = SecurityManager.hash_password(large_password)
        assert SecurityManager.verify_password(large_password, hashed)

        # Test with large token
        large_token = SecurityManager.generate_secure_token(100000)
        assert len(large_token) == 200000  # 100K bytes = 200K hex chars

        # Test with large file content
        large_content = b"x" * 1000000  # 1MB
        signature = SecurityManager.generate_file_signature(large_content, "key")
        assert len(signature) == 64

    def test_error_handling_robustness(self):
        """Test error handling robustness."""
        # Test with various problematic inputs
        try:
            # These should either work or fail gracefully
            SecurityManager.hash_password("normal_password")
            SecurityManager.generate_secure_token(32)
            SecurityManager.secure_compare("a", "b")
            SecurityManager.generate_file_signature(b"content", "key")
        except Exception as e:
            # If any exceptions occur, they should be reasonable
            assert isinstance(e, (ValueError, TypeError, AttributeError))


class TestSecurityManagerGlobalInstance:
    """Test the global security manager instance."""

    def test_global_instance_exists(self):
        """Test that global security manager instance exists."""
        assert security_manager is not None
        assert isinstance(security_manager, SecurityManager)

    def test_global_instance_functionality(self):
        """Test that global instance has all expected functionality."""
        # Test all methods are available
        assert hasattr(security_manager, "hash_password")
        assert hasattr(security_manager, "verify_password")
        assert hasattr(security_manager, "generate_secure_token")
        assert hasattr(security_manager, "secure_compare")
        assert hasattr(security_manager, "generate_file_signature")

        # Test methods are callable
        assert callable(security_manager.hash_password)
        assert callable(security_manager.verify_password)
        assert callable(security_manager.generate_secure_token)
        assert callable(security_manager.secure_compare)
        assert callable(security_manager.generate_file_signature)

    def test_global_instance_methods_work(self):
        """Test that global instance methods work correctly."""
        # Test basic functionality through global instance
        password = "global_test"
        hashed = security_manager.hash_password(password)
        assert security_manager.verify_password(password, hashed)

        token = security_manager.generate_secure_token()
        assert len(token) == 64

        assert security_manager.secure_compare("same", "same")
        assert not security_manager.secure_compare("different", "values")

        signature = security_manager.generate_file_signature(b"test", "key")
        assert len(signature) == 64

    def test_static_vs_instance_methods(self):
        """Test that static methods work the same as instance methods."""
        password = "static_test"

        # Static method calls
        static_hash = SecurityManager.hash_password(password)
        static_verified = SecurityManager.verify_password(password, static_hash)
        static_token = SecurityManager.generate_secure_token()
        static_compared = SecurityManager.secure_compare("test", "test")
        static_signature = SecurityManager.generate_file_signature(b"test", "key")

        # Instance method calls
        instance_hash = security_manager.hash_password(password)
        instance_verified = security_manager.verify_password(password, instance_hash)
        instance_token = security_manager.generate_secure_token()
        instance_compared = security_manager.secure_compare("test", "test")
        instance_signature = security_manager.generate_file_signature(b"test", "key")

        # Results should be functionally equivalent
        assert static_verified is True
        assert instance_verified is True
        assert len(static_token) == len(instance_token)
        assert static_compared == instance_compared
        assert len(static_signature) == len(instance_signature)

    def test_multiple_instances_independence(self):
        """Test that multiple instances work independently."""
        instance1 = SecurityManager()
        instance2 = SecurityManager()

        # Both instances should work independently
        password = "instance_test"
        hash1 = instance1.hash_password(password)
        hash2 = instance2.hash_password(password)

        # Hashes should be different (due to random salt)
        assert hash1 != hash2

        # But both should verify correctly
        assert instance1.verify_password(password, hash1)
        assert instance2.verify_password(password, hash2)

        # Cross-verification should also work
        assert instance1.verify_password(password, hash2)
        assert instance2.verify_password(password, hash1)


class TestSecurityManagerChildSafety:
    """Test SecurityManager for child safety and COPPA compliance."""

    def test_child_data_protection(self):
        """Test protection of child-related data."""
        # Simulate protecting child data
        child_data = {
            "child_id": "child_123",
            "name": "Test Child",
            "age": 8,
            "voice_data": "base64_encoded_voice",
            "chat_history": ["Hello", "How are you?"],
        }

        # Convert to bytes for signing
        child_data_bytes = str(child_data).encode("utf-8")

        # Generate secure key for child data
        child_key = SecurityManager.generate_secure_token()

        # Generate signature for integrity
        signature = SecurityManager.generate_file_signature(child_data_bytes, child_key)

        # Verify signature
        verification_signature = SecurityManager.generate_file_signature(
            child_data_bytes, child_key
        )
        assert SecurityManager.secure_compare(signature, verification_signature)

    def test_parental_password_security(self):
        """Test parental password security features."""
        # Test strong parental passwords
        parental_passwords = [
            "Parent@123!Strong",
            "VerySecureParentalPassword2024",
            "ComplexP@ssw0rd#ForChildSafety",
        ]

        for password in parental_passwords:
            hashed = SecurityManager.hash_password(password)

            # Should verify correctly
            assert SecurityManager.verify_password(password, hashed)

            # Should not verify with similar but wrong passwords
            assert not SecurityManager.verify_password(password + "x", hashed)
            assert not SecurityManager.verify_password(password.lower(), hashed)

    def test_session_token_security(self):
        """Test session token security for child interactions."""
        # Generate session tokens for child sessions
        session_tokens = [SecurityManager.generate_secure_token(32) for _ in range(10)]

        # All should be unique
        assert len(set(session_tokens)) == len(session_tokens)

        # All should be properly formatted
        for token in session_tokens:
            assert len(token) == 64  # 32 bytes = 64 hex chars
            assert all(c in "0123456789abcdef" for c in token)

    def test_child_content_signing(self):
        """Test signing of child-generated content."""
        # Simulate child-generated content that needs integrity protection
        child_contents = [
            b"Child's drawing data",
            b"Child's voice recording",
            b"Child's text message",
            b"Child's game progress",
            b"Child's preferences",
        ]

        content_key = SecurityManager.generate_secure_token()

        for content in child_contents:
            signature = SecurityManager.generate_file_signature(content, content_key)

            # Verify signature
            assert len(signature) == 64
            verification_signature = SecurityManager.generate_file_signature(
                content, content_key
            )
            assert SecurityManager.secure_compare(signature, verification_signature)

    def test_secure_child_data_comparison(self):
        """Test secure comparison of child data."""
        # Test secure comparison for child identifiers
        child_id1 = "child_123456"
        child_id2 = "child_123456"
        child_id3 = "child_789012"

        # Same IDs should match
        assert SecurityManager.secure_compare(child_id1, child_id2)

        # Different IDs should not match
        assert not SecurityManager.secure_compare(child_id1, child_id3)

        # Test with child session tokens
        session_token = SecurityManager.generate_secure_token()
        assert SecurityManager.secure_compare(session_token, session_token)

        different_token = SecurityManager.generate_secure_token()
        assert not SecurityManager.secure_compare(session_token, different_token)

    def test_coppa_compliance_features(self):
        """Test COPPA compliance features."""
        # Test secure handling of parental consent tokens
        consent_token = SecurityManager.generate_secure_token(
            64
        )  # Extra long for consent

        # Verify token properties
        assert len(consent_token) == 128  # 64 bytes = 128 hex chars
        assert all(c in "0123456789abcdef" for c in consent_token)

        # Test secure consent verification
        stored_consent = SecurityManager.hash_password(consent_token)
        assert SecurityManager.verify_password(consent_token, stored_consent)

        # Test consent data signing
        consent_data = b"Parental consent for child data collection"
        consent_key = SecurityManager.generate_secure_token()
        consent_signature = SecurityManager.generate_file_signature(
            consent_data, consent_key
        )

        # Verify consent signature
        assert len(consent_signature) == 64
        verification = SecurityManager.generate_file_signature(
            consent_data, consent_key
        )
        assert SecurityManager.secure_compare(consent_signature, verification)
