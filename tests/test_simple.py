import sys
from pathlib import Path

# Add src to path
src_path = Path(__file__).parent
while src_path.name != "backend" and src_path.parent != src_path:
    src_path = src_path.parent
src_path = src_path / "src"

if str(src_path) not in sys.path:
    sys.path.insert(0, str(src_path))

"""Simple test to verify pytest is working"""


try:
    import pytest
except ImportError as e:
    raise ImportError(
        "CRITICAL: pytest is required for production testing. "
        "Install with: pip install pytest pytest-asyncio"
    ) from e
from unittest.mock import MagicMock
import json


def test_basic_functionality():
    """Test basic functionality"""
    assert True


def test_encryption_mock():
    """Test encryption with mock"""
    # Mock encryption service
    encryption_service = MagicMock()
    encryption_service.encrypt.return_value = "encrypted_data"
    encryption_service.decrypt.return_value = "decrypted_data"

    # Test
    encrypted = encryption_service.encrypt("test_data")
    assert encrypted == "encrypted_data"

    decrypted = encryption_service.decrypt(encrypted)
    assert decrypted == "decrypted_data"


def test_json_operations():
    """Test JSON operations"""
    test_data = {"name": "Test Child", "age": 5, "language": "ar"}

    # Serialize and deserialize
    json_str = json.dumps(test_data)
    parsed_data = json.loads(json_str)

    assert parsed_data["name"] == "Test Child"
    assert parsed_data["age"] == 5
    assert parsed_data["language"] == "ar"


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
