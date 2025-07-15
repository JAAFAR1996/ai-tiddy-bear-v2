import sys
from pathlib import Path

# Add src to path
src_path = Path(__file__).parent
while src_path.name != "backend" and src_path.parent != src_path:
    src_path = src_path.parent
src_path = src_path / "src"

if str(src_path) not in sys.path:
    sys.path.insert(0, str(src_path))

import json
from datetime import datetime, timedelta

try:
    import pytest
except ImportError:
    try:
        from common.mock_pytest import pytest
    except ImportError:
        pass
        pass
    # Mock pytest when not available
    class MockPytest:
        def fixture(self, *args, **kwargs):
            def decorator(func):
                return func
            return decorator
        
        def mark(self):
            class MockMark:
                def parametrize(self, *args, **kwargs):
                    def decorator(func):
                        return func
                    return decorator
                
                def asyncio(self, func):
                    return func
                
                def slow(self, func):
                    return func
                
                def skip(self, reason=""):
                    def decorator(func):
                        return func
                    return decorator
            return MockMark()
        
        def raises(self, exception):
            class MockRaises:
                def __enter__(self):
                    return self
                def __exit__(self, *args):
                    return False
            return MockRaises()
        
        def skip(self, reason=""):
            def decorator(func):
                return func
            return decorator
    
    pytest = MockPytest()

try:
    from infrastructure.security.unified_encryption_service import EncryptionLevel
except ImportError:
    # If import fails, use mock versions
    class EncryptionLevel:
        BASIC = "basic"
        STANDARD = "standard"
        HIGH = "high"
        CRITICAL = "critical"


class TestUnifiedEncryptionService:
    """Test unified encryption service"""

    def test_simple_encryption(self, encryption_service):
        """Test simple encryption/decryption"""
        # Test data
        original_text = "مرحباً، هذا نص سري للأطفال"

        # Encrypt
        ciphertext, nonce = encryption_service.encrypt_simple(original_text)

        # Assert encrypted
        assert ciphertext != original_text
        assert nonce is not None
        assert len(ciphertext) > 0
        assert len(nonce) > 0

        # Decrypt
        decrypted = encryption_service.decrypt_simple(ciphertext, nonce)

        # Assert decrypted correctly
        assert decrypted == original_text

    @pytest.mark.asyncio
    async def test_advanced_encryption_levels(self, encryption_service):
        """Test different encryption levels"""
        test_data = {"name": "أحمد", "age": 5, "secret": "sensitive_info"}

        # Test each encryption level
        levels = [
            (EncryptionLevel.BASIC, 90),  # 90 days expiry
            (EncryptionLevel.STANDARD, 90),  # 90 days expiry
            (EncryptionLevel.HIGH, 30),  # 30 days expiry
            (EncryptionLevel.CRITICAL, 7),  # 7 days expiry
        ]

        for level, expiry_days in levels:
            # Encrypt
            encrypted = await encryption_service.encrypt(test_data, level=level)

            # Assertions
            assert encrypted.encryption_level == level
            assert encrypted.ciphertext is not None
            assert encrypted.key_id is not None

            # Check expiry
            if encrypted.expires_at:
                expected_expiry = datetime.utcnow() + timedelta(days=expiry_days)
                assert (
                    abs((encrypted.expires_at - expected_expiry).total_seconds()) < 60
                )

            # Decrypt
            decrypted = await encryption_service.decrypt(encrypted)
            decrypted_data = json.loads(decrypted.decode("utf-8"))

            # Assert decrypted correctly
            assert decrypted_data == test_data

    @pytest.mark.asyncio
    async def test_child_data_encryption(self, encryption_service):
        """Test child data encryption"""
        # Sensitive child data
        child_data = {
            "id": "child123",
            "name": "فاطمة محمد",
            "date_of_birth": "2019-05-15",
            "medical_info": {"allergies": ["peanuts"], "conditions": []},
            "personal_info": {"address": "123 Main St", "phone": "555-0123"},
            "conversations": ["conv1", "conv2", "conv3"],
            "public_id": "PUBLIC123",  # Non-sensitive field
        }

        # Encrypt child data
        encrypted_child_data = await encryption_service.encrypt_child_data(child_data)

        # Assert sensitive fields are encrypted
        assert "encrypted_name" in encrypted_child_data
        assert "encrypted_date_of_birth" in encrypted_child_data
        assert "encrypted_medical_info" in encrypted_child_data
        assert "encrypted_personal_info" in encrypted_child_data
        assert "encrypted_conversations" in encrypted_child_data

        # Assert non-sensitive fields remain
        assert encrypted_child_data["id"] == "child123"
        assert encrypted_child_data["public_id"] == "PUBLIC123"

        # Assert original sensitive fields are removed
        assert "name" not in encrypted_child_data
        assert "date_of_birth" not in encrypted_child_data

        # Decrypt child data
        decrypted_child_data = await encryption_service.decrypt_child_data(
            encrypted_child_data
        )

        # Assert all data recovered
        assert decrypted_child_data["name"] == "فاطمة محمد"
        assert decrypted_child_data["date_of_birth"] == "2019-05-15"
        assert decrypted_child_data["medical_info"]["allergies"] == ["peanuts"]

    @pytest.mark.asyncio
    async def test_audio_encryption(self, encryption_service):
        """Test audio data encryption"""
        # Mock audio data
        audio_data = b"RIFF....WAVEfmt...." + b"0" * 1000  # Simulated WAV file
        child_id = "child456"

        # Encrypt audio
        encrypted_audio = await encryption_service.encrypt_audio(audio_data, child_id)

        # Assertions
        assert encrypted_audio.encryption_level == EncryptionLevel.CRITICAL
        assert encrypted_audio.metadata["content_type"] == "audio"
        assert "child_id" in encrypted_audio.metadata
        # Should be hashed
        assert encrypted_audio.metadata["child_id"] != child_id

        # Decrypt audio
        decrypted_audio = await encryption_service.decrypt(encrypted_audio)

        # Assert audio data recovered
        assert decrypted_audio == audio_data

    @pytest.mark.asyncio
    async def test_encryption_expiry(self, encryption_service):
        """Test encryption expiry"""
        # Create expired encrypted data
        encrypted = await encryption_service.encrypt(
            "test data", level=EncryptionLevel.BASIC
        )
        encrypted.expires_at = datetime.utcnow() - timedelta(
            days=1
        )  # Expired yesterday

        # Try to decrypt expired data
        with pytest.raises(ValueError, match="Encrypted data has expired"):
            await encryption_service.decrypt(encrypted)

    def test_key_rotation(self, encryption_service):
        """Test key rotation"""
        # Add some keys to cache
        for i in range(5):
            key_id = f"key_{i}"
            encryption_service._generate_data_key(key_id, EncryptionLevel.STANDARD)

        # Check keys in cache
        assert len(encryption_service._key_cache) == 5

        # Manually expire some keys
        now = datetime.utcnow()
        for i, (key_id, (key, created_at)) in enumerate(
            encryption_service._key_cache.items()
        ):
            if i < 3:
                # Make first 3 keys expired
                encryption_service._key_cache[key_id] = (key, now - timedelta(days=31))

        # Rotate keys
        encryption_service.rotate_keys()

        # Assert expired keys removed
        assert len(encryption_service._key_cache) == 2
