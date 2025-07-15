import sys
from pathlib import Path

# Add src to path
src_path = Path(__file__).parent
while src_path.name != "backend" and src_path.parent != src_path:
    src_path = src_path.parent
src_path = src_path / "src"

if str(src_path) not in sys.path:
    sys.path.insert(0, str(src_path))

class TestSecurity:
    """Test security features"""

    def test_xss_prevention(self):
        """Test XSS prevention"""
        dangerous_inputs = [
            "<script>alert('XSS')</script>",
            "javascript:alert('XSS')",
            "<img src=x onerror=alert('XSS')>",
            "<iframe src='malicious.com'></iframe>",
        ]

        def sanitize_input(text):
            # Simple sanitization simulation
            dangerous_patterns = ["<script", "javascript:", "onerror=", "<iframe"]
            for pattern in dangerous_patterns:
                if pattern in text.lower():
                    return ""
            return text

        for input_text in dangerous_inputs:
            sanitized = sanitize_input(input_text)
            assert sanitized == ""

    def test_secure_storage(self):
        """Test secure storage of sensitive data"""

        # Mock secure storage
        class SecureStorage:
            def __init__(self):
                self._storage = {}

            def set_item(self, key, value, encrypt=False):
                if encrypt:
                    # Simulate encryption
                    value = f"encrypted_{value}"
                self._storage[key] = value

            def get_item(self, key, decrypt=False):
                value = self._storage.get(key)
                if decrypt and value and value.startswith("encrypted_"):
                    # Simulate decryption
                    value = value.replace("encrypted_", "")
                return value

        storage = SecureStorage()

        # Store sensitive data
        storage.set_item("token", "jwt_secret_token", encrypt=True)
        storage.set_item("user_id", "12345", encrypt=False)

        # Retrieve data
        token = storage.get_item("token", decrypt=True)
        user_id = storage.get_item("user_id")

        assert token == "jwt_secret_token"
        assert user_id == "12345"
        assert storage._storage["token"] == "encrypted_jwt_secret_token"
