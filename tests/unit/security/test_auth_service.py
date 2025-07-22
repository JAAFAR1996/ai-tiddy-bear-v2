import sys
from pathlib import Path

from src.infrastructure.security.core.real_auth_service import AuthService

# Add src to path
src_path = Path(__file__).parent
while src_path.name != "backend" and src_path.parent != src_path:
    src_path = src_path.parent
src_path = src_path / "src"

if str(src_path) not in sys.path:
    sys.path.insert(0, str(src_path))

"""
اختبارات خدمة المصادقة
"""

try:
    import pytest
except ImportError:
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


class TestAuthService:
    """اختبارات خدمة المصادقة"""

    def setup_method(self):
        """إعداد الاختبار"""
        self.auth_service = AuthService()

    def test_password_hashing(self):
        """اختبار تشفير كلمة المرور"""
        password = "test_password_123"
        hashed = self.auth_service.hash_password(password)

        assert hashed != password
        assert len(hashed) > 0
        assert self.auth_service.verify_password(password, hashed)

    def test_password_verification_fails_with_wrong_password(self):
        """اختبار فشل التحقق مع كلمة مرور خاطئة"""
        password = "correct_password"
        wrong_password = "wrong_password"
        hashed = self.auth_service.hash_password(password)

        assert not self.auth_service.verify_password(wrong_password, hashed)

    def test_access_token_creation(self):
        """اختبار إنشاء رمز الوصول"""
        user_data = {
            "sub": "user123",
            "email": "test@example.com",
            "role": "parent",
        }

        token = self.auth_service.create_access_token(user_data)

        assert isinstance(token, str)
        assert len(token) > 0

    def test_token_verification(self):
        """اختبار التحقق من الرمز"""
        user_data = {
            "sub": "user123",
            "email": "test@example.com",
            "role": "parent",
        }

        token = self.auth_service.create_access_token(user_data)
        decoded = self.auth_service.verify_token(token)

        assert decoded is not None
        assert decoded["sub"] == user_data["sub"]
        assert decoded["email"] == user_data["email"]
        assert decoded["role"] == user_data["role"]

    def test_invalid_token_verification(self):
        """اختبار التحقق من رمز غير صالح"""
        invalid_token = "invalid.token.here"
        decoded = self.auth_service.verify_token(invalid_token)

        assert decoded is None

    def test_user_authentication_success(self):
        """اختبار نجاح مصادقة المستخدم"""
        user = self.auth_service.authenticate_user(
            "parent@example.com", "TestSecurePass2025!"
        )  # ✅

        assert user is not None
        assert user["email"] == "parent@example.com"
        assert user["role"] == "parent"

    def test_user_authentication_failure(self):
        """اختبار فشل مصادقة المستخدم"""
        user = self.auth_service.authenticate_user(
            "nonexistent@example.com", "TestSecurePass2025!"
        )  # ✅
        assert user is None

        user = self.auth_service.authenticate_user(
            "parent@example.com", "wrong_password"
        )
        assert user is None
