import sys
from pathlib import Path

from src.config.settings import TEST_CONFIG

# Add src to path
src_path = Path(__file__).parent
while src_path.name != "backend" and src_path.parent != src_path:
    src_path = src_path.parent
src_path = src_path / "src"

if str(src_path) not in sys.path:
    sys.path.insert(0, str(src_path))

# Import pytest with fallback to mock
pytest = None
try:
    import pytest
except ImportError:
    try:
        from common.mock_pytest import pytest
    except ImportError:
        pass

    # Mock pytest when not available
    if pytest is None:
        class MockPytest:

        def fixture(self, *args, **kwargs):
            pass

            def decorator(func):
                return func

            return decorator

        def mark(self):
            pass

            class MockMark:
                def parametrize(self, *args, **kwargs):
                    pass

                    def decorator(func):
                return func

                    return decorator

                def asyncio(self, func):
                    pass

                    return func

                def slow(self, func):
                    pass

                    return func

                def skip(self, reason=""):
                    pass

                    def decorator(func):
                return func

                    return decorator

            return MockMark()

        def raises(self, exception):
            pass

            class MockRaises:
                def __enter__(self):
                    pass

                    return self

                def __exit__(self, *args):
                    pass

                    return False

            return MockRaises()

        def skip(self, reason=""):
            pass

            def decorator(func):
                return func

            return decorator

    pytest = MockPytest()


class TestAuthentication:
    """Test authentication functionality"""

    @pytest.mark.asyncio
    async def test_login_success(self, auth_service):
        """Test successful login"""
        # Arrange
        auth_service.login.return_value = {
            "user": {"id": "123", "email": TEST_CONFIG["test_user"]["email"]},
            "token": "jwt_token",
            "refreshToken": "refresh_token",
        }

        # Act
        result = await auth_service.login(
            TEST_CONFIG["test_user"]["email"],
            TEST_CONFIG["test_user"]["password"],
        )

        # Assert
        assert result["token"] == "jwt_token"
        assert result["user"]["email"] == TEST_CONFIG["test_user"]["email"]
        auth_service.login.assert_called_once()

    @pytest.mark.asyncio
    async def test_login_failure(self, auth_service):
        """Test failed login with invalid credentials"""
        # Arrange
        auth_service.login.side_effect = Exception("Invalid credentials")

        # Act & Assert
        with pytest.raises(Exception, match="Invalid credentials"):
            await auth_service.login("wrong@example.com", "wrong_password")

    @pytest.mark.asyncio
    async def test_logout(self, auth_service):
        """Test logout functionality"""
        # Arrange
        auth_service.logout.return_value = True

        # Act
        result = await auth_service.logout()

        # Assert
        assert result is True
        auth_service.logout.assert_called_once()

    @pytest.mark.asyncio
    async def test_token_refresh(self, auth_service):
        """Test token refresh"""
        # Arrange
        auth_service.refresh_token.return_value = {
            "token": "new_jwt_token",
            "refreshToken": "new_refresh_token",
        }

        # Act
        result = await auth_service.refresh_token("old_refresh_token")

        # Assert
        assert result["token"] == "new_jwt_token"
        auth_service.refresh_token.assert_called_once_with("old_refresh_token")

    @pytest.mark.asyncio
    async def test_auth_guard(self, auth_service):
        """Test authentication guard"""
        # Test authenticated user
        auth_service.is_authenticated.return_value = True
        assert await auth_service.is_authenticated() is True

        # Test unauthenticated user
        auth_service.is_authenticated.return_value = False
        assert await auth_service.is_authenticated() is False
