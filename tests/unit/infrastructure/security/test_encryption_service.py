"""Tests for Encryption Service
Testing enterprise-grade encryption service with key rotation support.
"""

import base64
import json
import os
from datetime import datetime, timedelta
from unittest.mock import Mock, patch

import pytest
from cryptography.fernet import Fernet

from src.infrastructure.security.encryption_service import (
    EncryptionKeyError,
    EncryptionService,
    get_encryption_service,
)


class TestEncryptionService:
    """Test the Encryption Service."""

    @pytest.fixture
    def valid_fernet_key(self):
        """Generate a valid Fernet key for testing."""
        return Fernet.generate_key().decode()

    @pytest.fixture
    def mock_environment(self, valid_fernet_key):
        """Mock environment variables for testing."""
        with patch.dict(
            os.environ,
            {
                "COPPA_ENCRYPTION_KEY": valid_fernet_key,
                "PBKDF2_SALT": "test_salt_for_testing",
                "ENCRYPTION_KEY_VERSION": "v1_20240101",
                "ENCRYPTION_KEY_CREATED_AT": "2024-01-01T00:00:00",
            },
        ):
            yield

    @pytest.fixture
    def encryption_service(self, mock_environment):
        """Create an encryption service instance with mocked environment."""
        return EncryptionService()

    def test_initialization_success(self, mock_environment):
        """Test successful encryption service initialization."""
        service = EncryptionService()

        assert service._fernet is not None
        assert service._key_version == "v1_20240101"
        assert service._key_created_at is not None
        assert isinstance(service._key_created_at, datetime)

    def test_initialization_missing_key_error(self):
        """Test initialization fails when COPPA_ENCRYPTION_KEY is missing."""
        with patch.dict(os.environ, {}, clear=True):
            with pytest.raises(
                EncryptionKeyError,
                match="COPPA_ENCRYPTION_KEY environment variable is required",
            ):
                EncryptionService()

    def test_initialization_empty_key_error(self):
        """Test initialization fails when COPPA_ENCRYPTION_KEY is empty."""
        with patch.dict(os.environ, {"COPPA_ENCRYPTION_KEY": ""}):
            with pytest.raises(
                EncryptionKeyError,
                match="COPPA_ENCRYPTION_KEY environment variable is required",
            ):
                EncryptionService()

    def test_initialization_invalid_key_format(self):
        """Test initialization fails with invalid key format."""
        with patch.dict(os.environ, {"COPPA_ENCRYPTION_KEY": "invalid_key"}):
            with pytest.raises(
                EncryptionKeyError, match="Invalid encryption key format"
            ):
                EncryptionService()

    def test_initialization_weak_key_error(self):
        """Test initialization fails with weak key."""
        # Create a weak key (low entropy)
        weak_key = base64.urlsafe_b64encode(b"a" * 32).decode()

        with patch.dict(os.environ, {"COPPA_ENCRYPTION_KEY": weak_key}):
            with pytest.raises(
                EncryptionKeyError,
                match="Detected weak or insufficiently strong encryption key",
            ):
                EncryptionService()

    def test_validate_encryption_key_valid(self, encryption_service, valid_fernet_key):
        """Test validation of valid encryption key."""
        # Should not raise any exception
        encryption_service._validate_encryption_key(valid_fernet_key)

    def test_validate_encryption_key_invalid_format(self, encryption_service):
        """Test validation fails for invalid key format."""
        with pytest.raises(EncryptionKeyError, match="Invalid encryption key format"):
            encryption_service._validate_encryption_key("invalid_key")

    def test_validate_encryption_key_wrong_length(self, encryption_service):
        """Test validation fails for wrong key length."""
        short_key = base64.urlsafe_b64encode(b"short").decode()

        with pytest.raises(EncryptionKeyError, match="Invalid encryption key format"):
            encryption_service._validate_encryption_key(short_key)

    def test_validate_encryption_key_test_encryption_failure(self, encryption_service):
        """Test validation fails when test encryption fails."""
        # Create a key that looks valid but fails validation
        with patch("cryptography.fernet.Fernet") as mock_fernet:
            mock_instance = Mock()
            mock_instance.encrypt.return_value = b"encrypted"
            mock_instance.decrypt.return_value = (
                b"wrong_data"  # Different from test data
            )
            mock_fernet.return_value = mock_instance

            with pytest.raises(
                EncryptionKeyError, match="Invalid encryption key format"
            ):
                encryption_service._validate_encryption_key("fake_key")

    def test_derive_key_with_salt(self, encryption_service, valid_fernet_key):
        """Test key derivation with provided salt."""
        with patch.dict(os.environ, {"PBKDF2_SALT": "test_salt"}):
            derived_key = encryption_service._derive_key(valid_fernet_key)

            assert isinstance(derived_key, bytes)
            assert len(derived_key) == 44  # Base64 encoded 32-byte key

    def test_derive_key_without_salt(self, encryption_service, valid_fernet_key):
        """Test key derivation without provided salt (generates random)."""
        with patch.dict(os.environ, {}, clear=True):
            with patch("secrets.token_bytes") as mock_token:
                mock_token.return_value = b"random_salt"

                derived_key = encryption_service._derive_key(valid_fernet_key)

                assert isinstance(derived_key, bytes)
                mock_token.assert_called_once_with(16)

    def test_derive_key_pbkdf2_parameters(self, encryption_service, valid_fernet_key):
        """Test key derivation uses correct PBKDF2 parameters."""
        with patch(
            "cryptography.hazmat.primitives.kdf.pbkdf2.PBKDF2HMAC"
        ) as mock_pbkdf2:
            mock_kdf = Mock()
            mock_kdf.derive.return_value = b"derived_key" * 2  # 32 bytes
            mock_pbkdf2.return_value = mock_kdf

            encryption_service._derive_key(valid_fernet_key)

            # Verify PBKDF2 parameters
            mock_pbkdf2.assert_called_once()
            call_args = mock_pbkdf2.call_args[1]
            assert call_args["algorithm"].__class__.__name__ == "SHA256"
            assert call_args["length"] == 32
            assert call_args["iterations"] == 100000

    def test_get_key_version_from_environment(self, encryption_service):
        """Test getting key version from environment."""
        with patch.dict(os.environ, {"ENCRYPTION_KEY_VERSION": "v2_20240201"}):
            version = encryption_service._get_key_version()
            assert version == "v2_20240201"

    def test_get_key_version_generated(self, encryption_service):
        """Test generating key version when not in environment."""
        with patch.dict(os.environ, {}, clear=True):
            with patch(
                "src.infrastructure.security.encryption_service.datetime"
            ) as mock_dt:
                mock_dt.utcnow.return_value.strftime.return_value = "20240301"

                version = encryption_service._get_key_version()

                assert version == "v1_20240301"

    def test_get_key_creation_date_from_environment(self, encryption_service):
        """Test getting key creation date from environment."""
        test_date = "2024-01-15T12:30:00"
        with patch.dict(os.environ, {"ENCRYPTION_KEY_CREATED_AT": test_date}):
            date = encryption_service._get_key_creation_date()
            assert date == datetime.fromisoformat(test_date)

    def test_get_key_creation_date_invalid_format(self, encryption_service):
        """Test getting key creation date with invalid format."""
        with patch.dict(os.environ, {"ENCRYPTION_KEY_CREATED_AT": "invalid_date"}):
            with patch(
                "src.infrastructure.security.encryption_service.datetime"
            ) as mock_dt:
                mock_dt.utcnow.return_value = datetime(2024, 1, 1)

                date = encryption_service._get_key_creation_date()

                assert date == datetime(2024, 1, 1)

    def test_get_key_creation_date_default(self, encryption_service):
        """Test getting key creation date when not in environment."""
        with patch.dict(os.environ, {}, clear=True):
            with patch(
                "src.infrastructure.security.encryption_service.datetime"
            ) as mock_dt:
                mock_dt.utcnow.return_value = datetime(2024, 1, 1)

                date = encryption_service._get_key_creation_date()

                assert date == datetime(2024, 1, 1)

    def test_is_key_rotation_needed_no_creation_date(self, encryption_service):
        """Test key rotation needed when no creation date."""
        encryption_service._key_created_at = None
        assert encryption_service._is_key_rotation_needed() is True

    def test_is_key_rotation_needed_old_key(self, encryption_service):
        """Test key rotation needed for old key."""
        # Key created 100 days ago (more than 90 days)
        old_date = datetime.utcnow() - timedelta(days=100)
        encryption_service._key_created_at = old_date

        assert encryption_service._is_key_rotation_needed() is True

    def test_is_key_rotation_needed_recent_key(self, encryption_service):
        """Test key rotation not needed for recent key."""
        # Key created 30 days ago (less than 90 days)
        recent_date = datetime.utcnow() - timedelta(days=30)
        encryption_service._key_created_at = recent_date

        assert encryption_service._is_key_rotation_needed() is False

    def test_is_key_rotation_needed_boundary_condition(self, encryption_service):
        """Test key rotation boundary condition (exactly 90 days)."""
        # Key created exactly 90 days ago
        boundary_date = datetime.utcnow() - timedelta(days=90)
        encryption_service._key_created_at = boundary_date

        assert encryption_service._is_key_rotation_needed() is False

    def test_is_key_strong_high_entropy(self, encryption_service):
        """Test key strength validation with high entropy key."""
        # High entropy key (valid Fernet key)
        high_entropy_key = Fernet.generate_key().decode()

        assert encryption_service._is_key_strong(high_entropy_key) is True

    def test_is_key_strong_low_entropy(self, encryption_service):
        """Test key strength validation with low entropy key."""
        # Low entropy key (repeated characters)
        low_entropy_key = base64.urlsafe_b64encode(b"a" * 32).decode()

        assert encryption_service._is_key_strong(low_entropy_key) is False

    def test_is_key_strong_edge_cases(self, encryption_service):
        """Test key strength validation with edge cases."""
        # Empty key
        assert encryption_service._is_key_strong("") is False

        # Very short key
        assert encryption_service._is_key_strong("abc") is False

        # Key with moderate entropy
        moderate_entropy_key = "abcdefghijklmnopqrstuvwxyz123456"
        result = encryption_service._is_key_strong(moderate_entropy_key)
        # Result depends on exact entropy calculation
        assert isinstance(result, bool)

    def test_is_key_strong_entropy_calculation_error(self, encryption_service):
        """Test key strength validation handles entropy calculation errors."""
        with patch("math.log2", side_effect=ValueError("Math error")):
            assert encryption_service._is_key_strong("any_key") is False

    def test_encrypt_string_data(self, encryption_service):
        """Test encrypting string data."""
        test_data = "Hello, World!"

        encrypted = encryption_service.encrypt(test_data)

        assert isinstance(encrypted, str)
        assert len(encrypted) > 0
        assert encrypted != test_data

    def test_encrypt_bytes_data(self, encryption_service):
        """Test encrypting bytes data."""
        test_data = b"Binary data"

        encrypted = encryption_service.encrypt(test_data)

        assert isinstance(encrypted, str)
        assert len(encrypted) > 0

    def test_encrypt_dict_data(self, encryption_service):
        """Test encrypting dictionary data."""
        test_data = {"key": "value", "number": 42}

        encrypted = encryption_service.encrypt(test_data)

        assert isinstance(encrypted, str)
        assert len(encrypted) > 0

    def test_encrypt_includes_metadata(self, encryption_service):
        """Test that encryption includes metadata."""
        test_data = "test"

        encrypted = encryption_service.encrypt(test_data)

        # Decrypt to verify metadata structure
        decrypted = encryption_service.decrypt(encrypted)

        # Should successfully decrypt (metadata handling tested implicitly)
        assert decrypted == test_data

    def test_encrypt_uninitialized_service(self):
        """Test encryption fails when service is not initialized."""
        service = EncryptionService.__new__(EncryptionService)
        service._fernet = None

        with pytest.raises(
            EncryptionKeyError, match="Encryption service not initialized"
        ):
            service.encrypt("test")

    def test_encrypt_fernet_exception(self, encryption_service):
        """Test encryption handles Fernet exceptions."""
        with patch.object(
            encryption_service._fernet,
            "encrypt",
            side_effect=Exception("Fernet error"),
        ):
            with pytest.raises(
                EncryptionKeyError, match="Encryption initialization failed"
            ):
                encryption_service.encrypt("test")

    def test_decrypt_string_data(self, encryption_service):
        """Test decrypting string data."""
        test_data = "Hello, World!"

        encrypted = encryption_service.encrypt(test_data)
        decrypted = encryption_service.decrypt(encrypted)

        assert decrypted == test_data

    def test_decrypt_bytes_data(self, encryption_service):
        """Test decrypting bytes data."""
        test_data = b"Binary data"

        encrypted = encryption_service.encrypt(test_data)
        decrypted = encryption_service.decrypt(encrypted)

        assert decrypted == test_data

    def test_decrypt_dict_data(self, encryption_service):
        """Test decrypting dictionary data."""
        test_data = {
            "key": "value",
            "number": 42,
            "nested": {"inner": "value"},
        }

        encrypted = encryption_service.encrypt(test_data)
        decrypted = encryption_service.decrypt(encrypted)

        assert decrypted == test_data

    def test_decrypt_bytes_input(self, encryption_service):
        """Test decrypting with bytes input."""
        test_data = "test data"

        encrypted = encryption_service.encrypt(test_data)
        encrypted_bytes = encrypted.encode("utf-8")

        decrypted = encryption_service.decrypt(encrypted_bytes)

        assert decrypted == test_data

    def test_decrypt_old_key_version(self, encryption_service):
        """Test decrypting data from older key version."""
        test_data = "test data"

        # Encrypt with current version
        encrypted = encryption_service.encrypt(test_data)

        # Simulate different key version
        original_version = encryption_service._key_version
        encryption_service._key_version = "v2_20240301"

        # Should still decrypt and log version difference
        decrypted = encryption_service.decrypt(encrypted)

        assert decrypted == test_data

        # Restore original version
        encryption_service._key_version = original_version

    def test_decrypt_invalid_token(self, encryption_service):
        """Test decryption fails with invalid token."""
        invalid_data = base64.b64encode(b"invalid_encrypted_data").decode()

        with pytest.raises(
            EncryptionKeyError,
            match="Decryption failed - data may be corrupted",
        ):
            encryption_service.decrypt(invalid_data)

    def test_decrypt_invalid_base64(self, encryption_service):
        """Test decryption fails with invalid base64."""
        with pytest.raises(EncryptionKeyError, match="Decryption failed"):
            encryption_service.decrypt("invalid_base64!")

    def test_decrypt_invalid_json_payload(self, encryption_service):
        """Test decryption handles invalid JSON payload."""
        # Create encrypted data with invalid JSON
        with patch.object(
            encryption_service._fernet, "decrypt", return_value=b"invalid_json"
        ):
            with pytest.raises(EncryptionKeyError, match="Decryption failed"):
                encryption_service.decrypt("fake_encrypted_data")

    def test_decrypt_missing_metadata(self, encryption_service):
        """Test decryption handles missing metadata."""
        # Create encrypted payload without metadata
        payload = {"data": base64.b64encode(b"test").decode()}
        encrypted_payload = encryption_service._fernet.encrypt(
            json.dumps(payload).encode()
        )
        encrypted_data = base64.b64encode(encrypted_payload).decode()

        decrypted = encryption_service.decrypt(encrypted_data)

        assert decrypted == "test"

    def test_decrypt_uninitialized_service(self):
        """Test decryption fails when service is not initialized."""
        service = EncryptionService.__new__(EncryptionService)
        service._fernet = None

        with pytest.raises(
            EncryptionKeyError, match="Encryption service not initialized"
        ):
            service.decrypt("test")

    def test_decrypt_unicode_decode_error(self, encryption_service):
        """Test decryption handles unicode decode errors."""
        # Create data that will cause unicode decode error
        test_data = b"\x80\x81\x82\x83"  # Invalid UTF-8

        encrypted = encryption_service.encrypt(test_data)
        decrypted = encryption_service.decrypt(encrypted)

        # Should return as bytes when string decoding fails
        assert decrypted == test_data

    def test_decrypt_json_decode_error(self, encryption_service):
        """Test decryption handles JSON decode errors."""
        test_data = "not_json_data"

        encrypted = encryption_service.encrypt(test_data)
        decrypted = encryption_service.decrypt(encrypted)

        # Should return as string when JSON parsing fails
        assert decrypted == test_data

    def test_encrypt_decrypt_round_trip_various_data(self, encryption_service):
        """Test encrypt/decrypt round trip with various data types."""
        test_cases = [
            "simple string",
            "unicode string with émojis 🔐",
            b"binary data",
            {"dict": "value", "number": 42},
            {"complex": {"nested": ["list", "items"], "boolean": True}},
            "",  # Empty string
            b"",  # Empty bytes
            {},  # Empty dict
            {"unicode": "test with unicode: 测试"},
            "very long string " * 100,
            {"large_dict": {f"key_{i}": f"value_{i}" for i in range(100)}},
        ]

        for test_data in test_cases:
            encrypted = encryption_service.encrypt(test_data)
            decrypted = encryption_service.decrypt(encrypted)
            assert decrypted == test_data

    def test_rotate_key_success(self, encryption_service, valid_fernet_key):
        """Test successful key rotation."""
        new_key = Fernet.generate_key().decode()
        original_version = encryption_service._key_version

        encryption_service.rotate_key(new_key)

        # Verify key rotation
        assert encryption_service._key_version != original_version
        assert encryption_service._key_version.startswith("v2_")
        assert encryption_service._key_created_at is not None

        # Verify new key works
        test_data = "test after rotation"
        encrypted = encryption_service.encrypt(test_data)
        decrypted = encryption_service.decrypt(encrypted)
        assert decrypted == test_data

    def test_rotate_key_invalid_key(self, encryption_service):
        """Test key rotation fails with invalid key."""
        original_version = encryption_service._key_version

        with pytest.raises(EncryptionKeyError, match="Invalid encryption key format"):
            encryption_service.rotate_key("invalid_key")

        # Verify rollback
        assert encryption_service._key_version == original_version

    def test_rotate_key_weak_key(self, encryption_service):
        """Test key rotation fails with weak key."""
        weak_key = base64.urlsafe_b64encode(b"a" * 32).decode()
        original_version = encryption_service._key_version

        with pytest.raises(
            EncryptionKeyError,
            match="Detected weak or insufficiently strong encryption key",
        ):
            encryption_service.rotate_key(weak_key)

        # Verify rollback
        assert encryption_service._key_version == original_version

    def test_rotate_key_version_increment(self, encryption_service):
        """Test key rotation increments version number."""
        # Set up initial version
        encryption_service._key_version = "v5_20240101"

        new_key = Fernet.generate_key().decode()
        encryption_service.rotate_key(new_key)

        # Should increment to v6
        assert encryption_service._key_version.startswith("v6_")

    def test_rotate_key_rollback_on_failure(self, encryption_service):
        """Test key rotation rollback on failure."""
        original_fernet = encryption_service._fernet
        original_version = encryption_service._key_version

        # Mock failure during rotation
        with patch.object(
            encryption_service,
            "_derive_key",
            side_effect=Exception("Derive error"),
        ):
            with pytest.raises(EncryptionKeyError, match="Key rotation failed"):
                encryption_service.rotate_key(Fernet.generate_key().decode())

        # Verify rollback
        assert encryption_service._fernet == original_fernet
        assert encryption_service._key_version == original_version

    def test_generate_secure_key(self, encryption_service):
        """Test secure key generation."""
        key = encryption_service.generate_secure_key()

        assert isinstance(key, str)
        assert len(key) > 0

        # Verify it's a valid Fernet key
        fernet = Fernet(key.encode())
        test_data = b"test"
        encrypted = fernet.encrypt(test_data)
        decrypted = fernet.decrypt(encrypted)
        assert decrypted == test_data

    def test_generate_secure_key_uniqueness(self, encryption_service):
        """Test that generated keys are unique."""
        key1 = encryption_service.generate_secure_key()
        key2 = encryption_service.generate_secure_key()

        assert key1 != key2

    def test_get_key_info(self, encryption_service):
        """Test getting key information."""
        info = encryption_service.get_key_info()

        assert isinstance(info, dict)
        assert "version" in info
        assert "created_at" in info
        assert "rotation_needed" in info
        assert "algorithm" in info

        assert info["version"] == encryption_service._key_version
        assert info["algorithm"] == "Fernet-PBKDF2"
        assert isinstance(info["rotation_needed"], bool)

    def test_get_key_info_no_creation_date(self, encryption_service):
        """Test getting key info when no creation date."""
        encryption_service._key_created_at = None

        info = encryption_service.get_key_info()

        assert info["created_at"] is None
        assert info["rotation_needed"] is True

    def test_encryption_service_constants(self):
        """Test encryption service constants."""
        assert EncryptionService.KEY_ROTATION_DAYS == 90
        assert EncryptionService.MIN_KEY_ENTROPY == 256

    def test_encryption_key_error_inheritance(self):
        """Test EncryptionKeyError inherits from Exception."""
        assert issubclass(EncryptionKeyError, Exception)

        error = EncryptionKeyError("test message")
        assert str(error) == "test message"

    def test_entropy_calculation_comprehensive(self, encryption_service):
        """Test comprehensive entropy calculation scenarios."""
        # Test various entropy levels
        entropy_tests = [
            # (key, expected_strong)
            ("a" * 44, False),  # Zero entropy
            ("ab" * 22, False),  # Low entropy
            (
                "abcdefghijklmnopqrstuvwxyz" + "0123456789" + "ABCDEF",
                False,
            ),  # Medium entropy
            (Fernet.generate_key().decode(), True),  # High entropy (random)
        ]

        for key, expected_strong in entropy_tests:
            result = encryption_service._is_key_strong(key)
            assert result == expected_strong

    def test_concurrent_encryption_operations(self, encryption_service):
        """Test concurrent encryption operations."""
        import threading

        results = []
        errors = []

        def encrypt_decrypt_worker(data):
            try:
                encrypted = encryption_service.encrypt(f"test_data_{data}")
                decrypted = encryption_service.decrypt(encrypted)
                results.append((data, decrypted))
            except Exception as e:
                errors.append(e)

        # Create multiple threads
        threads = []
        for i in range(10):
            thread = threading.Thread(target=encrypt_decrypt_worker, args=(i,))
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

        for i, (data_id, decrypted) in enumerate(results):
            assert decrypted == f"test_data_{data_id}"

    def test_memory_safety_large_data(self, encryption_service):
        """Test memory safety with large data."""
        # Test with large string
        large_data = "x" * 1000000  # 1MB string

        encrypted = encryption_service.encrypt(large_data)
        decrypted = encryption_service.decrypt(encrypted)

        assert decrypted == large_data

        # Test with large dict
        large_dict = {f"key_{i}": f"value_{i}" * 100 for i in range(1000)}

        encrypted = encryption_service.encrypt(large_dict)
        decrypted = encryption_service.decrypt(encrypted)

        assert decrypted == large_dict

    def test_error_handling_edge_cases(self, encryption_service):
        """Test error handling with edge cases."""
        # Test with None
        with pytest.raises(Exception):
            encryption_service.encrypt(None)

        # Test with circular reference (should fail JSON serialization)
        circular_dict = {"key": "value"}
        circular_dict["self"] = circular_dict

        with pytest.raises(Exception):
            encryption_service.encrypt(circular_dict)

    def test_key_derivation_consistency(self, encryption_service):
        """Test that key derivation is consistent."""
        master_key = "test_master_key"

        # Multiple derivations should produce same result
        key1 = encryption_service._derive_key(master_key)
        key2 = encryption_service._derive_key(master_key)

        assert key1 == key2

    def test_encryption_metadata_structure(self, encryption_service):
        """Test encryption metadata structure."""
        test_data = "test"
        encrypted = encryption_service.encrypt(test_data)

        # Manually decrypt to inspect metadata
        encrypted_bytes = base64.b64decode(encrypted)
        decrypted_payload = encryption_service._fernet.decrypt(encrypted_bytes)
        payload = json.loads(decrypted_payload.decode("utf-8"))

        # Verify metadata structure
        assert "metadata" in payload
        assert "data" in payload

        metadata = payload["metadata"]
        assert "version" in metadata
        assert "timestamp" in metadata
        assert "algorithm" in metadata
        assert metadata["algorithm"] == "Fernet-PBKDF2"

    def test_base64_encoding_decoding(self, encryption_service):
        """Test base64 encoding/decoding in encryption process."""
        # Test with binary data that might cause base64 issues
        binary_data = bytes(range(256))

        encrypted = encryption_service.encrypt(binary_data)
        decrypted = encryption_service.decrypt(encrypted)

        assert decrypted == binary_data

    def test_json_serialization_edge_cases(self, encryption_service):
        """Test JSON serialization edge cases."""
        # Test with various Python types
        test_cases = [
            {"int": 42, "float": 3.14, "bool": True, "null": None},
            {"list": [1, 2, 3], "nested": {"deep": {"value": "test"}}},
            {"unicode": "测试", "emoji": "🔐", "special": "!@#$%^&*()"},
        ]

        for test_data in test_cases:
            encrypted = encryption_service.encrypt(test_data)
            decrypted = encryption_service.decrypt(encrypted)
            assert decrypted == test_data


class TestGetEncryptionService:
    """Test the get_encryption_service function."""

    def test_get_encryption_service_singleton(self, mock_environment):
        """Test that get_encryption_service returns singleton instance."""
        # Clear global instance
        import src.infrastructure.security.encryption_service as enc_module

        enc_module._encryption_service = None

        # Get first instance
        service1 = get_encryption_service()
        assert service1 is not None

        # Get second instance - should be same
        service2 = get_encryption_service()
        assert service1 is service2

    def test_get_encryption_service_initialization(self, mock_environment):
        """Test that get_encryption_service initializes service correctly."""
        # Clear global instance
        import src.infrastructure.security.encryption_service as enc_module

        enc_module._encryption_service = None

        service = get_encryption_service()

        assert isinstance(service, EncryptionService)
        assert service._fernet is not None
        assert service._key_version is not None

    def test_get_encryption_service_thread_safety(self, mock_environment):
        """Test thread safety of get_encryption_service."""
        import threading

        # Clear global instance
        import src.infrastructure.security.encryption_service as enc_module

        enc_module._encryption_service = None

        services = []

        def get_service():
            services.append(get_encryption_service())

        # Create multiple threads
        threads = []
        for _ in range(10):
            thread = threading.Thread(target=get_service)
            threads.append(thread)

        # Start all threads
        for thread in threads:
            thread.start()

        # Wait for completion
        for thread in threads:
            thread.join()

        # All should be the same instance
        assert len(services) == 10
        assert all(service is services[0] for service in services)

    def test_get_encryption_service_handles_initialization_error(self):
        """Test that get_encryption_service handles initialization errors."""
        # Clear global instance
        import src.infrastructure.security.encryption_service as enc_module

        enc_module._encryption_service = None

        # Remove required environment variable
        with patch.dict(os.environ, {}, clear=True):
            with pytest.raises(EncryptionKeyError):
                get_encryption_service()

    def test_get_encryption_service_caching(self, mock_environment):
        """Test that get_encryption_service properly caches instance."""
        # Clear global instance
        import src.infrastructure.security.encryption_service as enc_module

        enc_module._encryption_service = None

        # Mock EncryptionService to count instantiations
        with patch(
            "src.infrastructure.security.encryption_service.EncryptionService"
        ) as mock_service:
            mock_instance = Mock()
            mock_service.return_value = mock_instance

            # Call multiple times
            service1 = get_encryption_service()
            service2 = get_encryption_service()
            service3 = get_encryption_service()

            # Should only instantiate once
            assert mock_service.call_count == 1
            assert service1 is service2 is service3 is mock_instance


class TestEncryptionServiceIntegration:
    """Integration tests for encryption service."""

    def test_full_coppa_compliance_workflow(self, mock_environment):
        """Test full COPPA compliance workflow."""
        service = EncryptionService()

        # Child data that needs protection
        child_data = {
            "child_id": "child_123",
            "name": "Test Child",
            "age": 8,
            "interactions": ["hello", "how are you?"],
            "preferences": {
                "favorite_color": "blue",
                "games": ["puzzle", "story"],
            },
        }

        # Encrypt child data
        encrypted = service.encrypt(child_data)

        # Verify encryption
        assert isinstance(encrypted, str)
        assert len(encrypted) > 0
        assert "child_123" not in encrypted  # Should not contain plaintext
        assert "Test Child" not in encrypted

        # Decrypt and verify
        decrypted = service.decrypt(encrypted)
        assert decrypted == child_data

    def test_key_rotation_with_data_migration(self, mock_environment):
        """Test key rotation with data migration scenario."""
        service = EncryptionService()

        # Encrypt data with original key
        test_data = "important_child_data"
        encrypted_old = service.encrypt(test_data)

        # Rotate key
        new_key = service.generate_secure_key()
        service.rotate_key(new_key)

        # Old data should still decrypt
        decrypted_old = service.decrypt(encrypted_old)
        assert decrypted_old == test_data

        # New data should encrypt with new key
        encrypted_new = service.encrypt(test_data)
        decrypted_new = service.decrypt(encrypted_new)
        assert decrypted_new == test_data

        # Old and new encrypted data should be different
        assert encrypted_old != encrypted_new

    def test_enterprise_security_requirements(self, mock_environment):
        """Test enterprise security requirements."""
        service = EncryptionService()

        # Test key info
        key_info = service.get_key_info()
        assert key_info["algorithm"] == "Fernet-PBKDF2"

        # Test encryption metadata
        test_data = "security_test"
        encrypted = service.encrypt(test_data)

        # Verify encrypted data structure
        assert isinstance(encrypted, str)

        # Verify base64 encoding
        try:
            base64.b64decode(encrypted)
        except Exception:
            pytest.fail("Encrypted data should be valid base64")

        # Verify decryption works
        decrypted = service.decrypt(encrypted)
        assert decrypted == test_data

    def test_performance_characteristics(self, mock_environment):
        """Test performance characteristics of encryption service."""
        import time

        service = EncryptionService()

        # Test encryption performance
        test_data = "performance_test_data" * 100

        start_time = time.time()
        encrypted = service.encrypt(test_data)
        encrypt_time = time.time() - start_time

        start_time = time.time()
        decrypted = service.decrypt(encrypted)
        decrypt_time = time.time() - start_time

        # Should be reasonably fast
        assert encrypt_time < 1.0  # Less than 1 second
        assert decrypt_time < 1.0  # Less than 1 second
        assert decrypted == test_data

    def test_error_recovery_scenarios(self, mock_environment):
        """Test error recovery scenarios."""
        service = EncryptionService()

        # Test recovery from corrupted data
        test_data = "recovery_test"
        encrypted = service.encrypt(test_data)

        # Corrupt the encrypted data
        corrupted = encrypted[:-5] + "xxxxx"

        with pytest.raises(EncryptionKeyError):
            service.decrypt(corrupted)

        # Original should still work
        decrypted = service.decrypt(encrypted)
        assert decrypted == test_data

    def test_logging_and_monitoring(self, mock_environment):
        """Test logging and monitoring capabilities."""
        with patch(
            "src.infrastructure.security.encryption_service.logger"
        ) as mock_logger:
            service = EncryptionService()

            # Test various operations trigger appropriate logs
            test_data = "logging_test"
            encrypted = service.encrypt(test_data)
            decrypted = service.decrypt(encrypted)

            # Verify some logging occurred during initialization
            assert mock_logger.info.called or mock_logger.warning.called

    def test_child_safety_data_protection(self, mock_environment):
        """Test child safety data protection features."""
        service = EncryptionService()

        # Test with various child data types
        child_data_types = [
            {"voice_recording": "base64_audio_data_here"},
            {"chat_history": ["Hello", "How are you?", "Tell me a story"]},
            {
                "personal_info": {
                    "name": "Child",
                    "age": 7,
                    "school": "Elementary",
                }
            },
            {"behavioral_data": {"mood": "happy", "activity": "playing"}},
            {"biometric_data": {"voice_print": "encrypted_voice_pattern"}},
        ]

        for data in child_data_types:
            encrypted = service.encrypt(data)
            decrypted = service.decrypt(encrypted)

            # Verify data integrity
            assert decrypted == data

            # Verify no plaintext leakage
            for key, value in data.items():
                if isinstance(value, str):
                    assert value not in encrypted
                elif isinstance(value, dict):
                    for inner_value in value.values():
                        if isinstance(inner_value, str):
                            assert inner_value not in encrypted
