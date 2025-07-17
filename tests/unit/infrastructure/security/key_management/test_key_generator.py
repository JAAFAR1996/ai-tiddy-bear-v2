"""
Test Key Generator

Comprehensive unit tests for KeyGenerator with algorithm coverage and child data security.
"""

import pytest
from unittest.mock import patch
from src.infrastructure.security.key_management.key_generator import KeyGenerator
from src.infrastructure.security.key_rotation_service import KeyType


@pytest.fixture
def key_generator():
    """Create KeyGenerator instance."""
    return KeyGenerator()


class TestKeyGeneration:
    """Test key generation functionality."""

    def test_generate_aes_256_key(self, key_generator):
        """Test AES-256 key generation."""
        # Act
        key_id, key_data = key_generator.generate_key(
            KeyType.ENCRYPTION, "AES-256")

        # Assert
        assert key_id is not None
        assert KeyType.ENCRYPTION.value in key_id
        assert isinstance(key_data, bytes)
        assert len(key_data) == 32  # 256 bits = 32 bytes

    def test_generate_aes_128_key(self, key_generator):
        """Test AES-128 key generation."""
        # Act
        key_id, key_data = key_generator.generate_key(
            KeyType.SESSION, "AES-128")

        # Assert
        assert key_id is not None
        assert KeyType.SESSION.value in key_id
        assert isinstance(key_data, bytes)
        assert len(key_data) == 16  # 128 bits = 16 bytes

    def test_generate_chacha20_key(self, key_generator):
        """Test ChaCha20 key generation."""
        # Act
        key_id, key_data = key_generator.generate_key(
            KeyType.SIGNING, "ChaCha20")

        # Assert
        assert key_id is not None
        assert KeyType.SIGNING.value in key_id
        assert isinstance(key_data, bytes)
        assert len(key_data) == 32  # 256 bits = 32 bytes

    def test_generate_child_data_key_uses_chacha20(self, key_generator):
        """Test that child data keys always use ChaCha20 for enhanced security."""
        # Act
        key_id, key_data = key_generator.generate_key(
            KeyType.CHILD_DATA, "AES-256")

        # Assert
        assert key_id is not None
        assert KeyType.CHILD_DATA.value in key_id
        assert isinstance(key_data, bytes)
        assert len(key_data) == 32  # ChaCha20 uses 256 bits

    def test_key_id_format(self, key_generator):
        """Test key ID format includes type, timestamp, and random suffix."""
        # Act
        key_id, _ = key_generator.generate_key(KeyType.JWT, "AES-256")

        # Assert
        parts = key_id.split("_")
        assert len(parts) >= 4  # type_YYYYMMDD_HHMMSS_suffix
        assert parts[0] == KeyType.JWT.value
        assert len(parts[1]) == 8  # YYYYMMDD
        assert len(parts[2]) == 6  # HHMMSS
        assert len(parts[3]) == 8  # hex suffix

    def test_generate_key_unsupported_algorithm(self, key_generator):
        """Test key generation with unsupported algorithm."""
        # Act & Assert
        with pytest.raises(ValueError, match="Unsupported algorithm"):
            key_generator.generate_key(KeyType.ENCRYPTION, "DES")

    def test_key_uniqueness(self, key_generator):
        """Test that generated keys are unique."""
        # Generate multiple keys
        keys = []
        for _ in range(10):
            key_id, key_data = key_generator.generate_key(
                KeyType.SESSION, "AES-256")
            keys.append((key_id, key_data))

        # Check uniqueness
        key_ids = [k[0] for k in keys]
        key_datas = [k[1] for k in keys]

        assert len(set(key_ids)) == 10  # All IDs unique
        assert len(set(key_datas)) == 10  # All key data unique

    def test_all_key_types(self, key_generator):
        """Test key generation for all key types."""
        for key_type in KeyType:
            key_id, key_data = key_generator.generate_key(key_type, "AES-256")

            assert key_id is not None
            assert key_type.value in key_id
            assert isinstance(key_data, bytes)
            assert len(key_data) > 0


class TestKeyGeneratorEdgeCases:
    """Test edge cases and security scenarios."""

    def test_concurrent_key_generation(self, key_generator):
        """Test concurrent key generation produces unique keys."""
        import threading

        results = []

        def generate_key():
            key_id, key_data = key_generator.generate_key(
                KeyType.ENCRYPTION, "AES-256")
            results.append((key_id, key_data))

        # Create multiple threads
        threads = []
        for _ in range(5):
            t = threading.Thread(target=generate_key)
            threads.append(t)
            t.start()

        # Wait for all threads
        for t in threads:
            t.join()

        # Check all keys are unique
        assert len(results) == 5
        key_ids = [r[0] for r in results]
        assert len(set(key_ids)) == 5

    def test_algorithm_key_sizes_consistency(self, key_generator):
        """Test that algorithm key sizes are consistent."""
        # Test multiple generations of same algorithm
        for _ in range(5):
            _, key_data = key_generator.generate_key(
                KeyType.ENCRYPTION, "AES-256")
            assert len(key_data) == 32

        for _ in range(5):
            _, key_data = key_generator.generate_key(
                KeyType.SESSION, "AES-128")
            assert len(key_data) == 16

        for _ in range(5):
            _, key_data = key_generator.generate_key(
                KeyType.SIGNING, "ChaCha20")
            assert len(key_data) == 32

    @patch("secrets.token_bytes")
    def test_key_generation_failure_handling(
            self, mock_token_bytes, key_generator):
        """Test handling of key generation failures."""
        # Mock failure
        mock_token_bytes.side_effect = Exception("Random generation failed")

        # Act & Assert
        with pytest.raises(Exception, match="Random generation failed"):
            key_generator.generate_key(KeyType.ENCRYPTION, "AES-256")
