"""Comprehensive Unit Tests for Production Auth Service"""

from datetime import datetime, timedelta
from unittest.mock import AsyncMock
from uuid import uuid4

import pytest
from fastapi import HTTPException, status
from jose import jwt

from src.infrastructure.security.auth.real_auth_service import (
    ProductionAuthService,
)
from src.domain.models.validation_models import (
    LoginRequest,
    LoginResponse,
)


@pytest.fixture
def auth_service():
    """Create auth service instance for testing with dynamically generated keys."""
    import secrets

    service = ProductionAuthService()
    # Generate secure test key dynamically - never hardcode
    service.secret_key = secrets.token_urlsafe(32)  # ✅  - مفتاح ديناميكي آمن
    return service


@pytest.fixture
def mock_redis():
    """Create mock Redis cache."""
    redis = AsyncMock()
    redis.get = AsyncMock(return_value=None)
    redis.setex = AsyncMock(return_value=True)
    redis.delete = AsyncMock(return_value=True)
    return redis


@pytest.fixture
def mock_database():
    """Create mock database."""
    db = AsyncMock()
    return db


@pytest.fixture
def sample_user():
    """Create sample user data."""
    return {
        "id": str(uuid4()),
        "email": "parent@test.com",
        "role": "parent",
        "name": "Test Parent",
        "is_active": True,
        "created_at": datetime.utcnow(),
        # "TestSecurePass2025!"  # ✅
        "password_hash": "$2b$12$KIXSGTyIgE7h8DVPZX.5NOCjGz2xEt7FLWXB5v7Y8Kj3TjKjH5K8a",
    }


class TestPasswordHashing:
    """Test password hashing functionality."""

    def test_hash_password_success(self, auth_service):
        """Test successful password hashing."""
        password = "SecurePassword123!"
        hashed = auth_service.hash_password(password)

        assert hashed is not None
        assert hashed != password
        assert hashed.startswith("$2b$")
        assert len(hashed) > 50

    def test_hash_password_too_short(self, auth_service):
        """Test password hashing with too short password."""
        with pytest.raises(ValueError, match="at least 8 characters"):
            auth_service.hash_password("short")

    def test_verify_password_correct(self, auth_service):
        """Test password verification with correct password."""
        password = "TestPassword123!"
        hashed = auth_service.hash_password(password)

        assert auth_service.verify_password(password, hashed) is True

    def test_verify_password_incorrect(self, auth_service):
        """Test password verification with incorrect password."""
        password = "TestPassword123!"
        hashed = auth_service.hash_password(password)

        assert auth_service.verify_password("WrongPassword", hashed) is False

    def test_verify_password_invalid_hash(self, auth_service):
        """Test password verification with invalid hash."""
        assert auth_service.verify_password("password", "invalid_hash") is False


class TestTokenManagement:
    """Test JWT token creation and verification."""

    def test_create_access_token(self, auth_service, sample_user):
        """Test access token creation."""
        token = auth_service.create_access_token(sample_user)

        assert token is not None
        assert isinstance(token, str)

        # Decode and verify token
        payload = jwt.decode(
            token, auth_service.secret_key, algorithms=[auth_service.algorithm]
        )

        assert payload["sub"] == sample_user["id"]
        assert payload["email"] == sample_user["email"]
        assert payload["role"] == sample_user["role"]
        assert payload["type"] == "access"
        assert "exp" in payload
        assert "iat" in payload

    def test_create_refresh_token(self, auth_service, sample_user):
        """Test refresh token creation."""
        token = auth_service.create_refresh_token(sample_user)

        assert token is not None
        assert isinstance(token, str)

        # Decode and verify token
        payload = jwt.decode(
            token, auth_service.secret_key, algorithms=[auth_service.algorithm]
        )

        assert payload["sub"] == sample_user["id"]
        assert payload["email"] == sample_user["email"]
        assert payload["type"] == "refresh"
        assert "exp" in payload
        assert "iat" in payload

    @pytest.mark.asyncio
    async def test_verify_token_valid(self, auth_service, sample_user):
        """Test token verification with valid token."""
        token = auth_service.create_access_token(sample_user)

        payload = await auth_service.verify_token(token)

        assert payload is not None
        assert payload["sub"] == sample_user["id"]
        assert payload["email"] == sample_user["email"]

    @pytest.mark.asyncio
    async def test_verify_token_expired(self, auth_service, sample_user):
        """Test token verification with expired token."""
        # Create token with past expiration
        past_time = datetime.utcnow() - timedelta(hours=1)
        token_data = {
            "sub": sample_user["id"],
            "email": sample_user["email"],
            "role": sample_user["role"],
            "type": "access",
            "iat": past_time,
            "exp": past_time,
        }

        expired_token = jwt.encode(
            token_data,
            auth_service.secret_key,
            algorithm=auth_service.algorithm,
        )

        payload = await auth_service.verify_token(expired_token)
        assert payload is None

    @pytest.mark.asyncio
    async def test_verify_token_invalid(self, auth_service):
        """Test token verification with invalid token."""
        payload = await auth_service.verify_token("invalid.token.here")
        assert payload is None

    @pytest.mark.asyncio
    async def test_verify_token_blacklisted(
        self, auth_service, sample_user, mock_redis
    ):
        """Test token verification with blacklisted token."""
        auth_service.redis_cache = mock_redis
        token = auth_service.create_access_token(sample_user)

        # Mock token as blacklisted
        mock_redis.get.return_value = "1"

        payload = await auth_service.verify_token(token)
        assert payload is None
        mock_redis.get.assert_called_once_with(f"blacklist:{token}")


class TestRateLimiting:
    """Test rate limiting and account lockout."""

    @pytest.mark.asyncio
    async def test_check_rate_limit_allowed(self, auth_service):
        """Test rate limit check when attempts are allowed."""
        email = "test@example.com"

        allowed = await auth_service.check_rate_limit(email)
        assert allowed is True

    @pytest.mark.asyncio
    async def test_check_rate_limit_exceeded(self, auth_service):
        """Test rate limit check when attempts exceeded."""
        email = "test@example.com"

        # Add maximum failed attempts
        for _ in range(auth_service.max_login_attempts):
            await auth_service.record_failed_login(email)

        allowed = await auth_service.check_rate_limit(email)
        assert allowed is False
        assert email in auth_service.locked_accounts

    @pytest.mark.asyncio
    async def test_check_rate_limit_unlock_after_duration(self, auth_service):
        """Test account unlock after lockout duration."""
        email = "test@example.com"

        # Lock the account
        auth_service.locked_accounts[email] = datetime.utcnow() - timedelta(hours=2)

        allowed = await auth_service.check_rate_limit(email)
        assert allowed is True
        assert email not in auth_service.locked_accounts

    @pytest.mark.asyncio
    async def test_record_failed_login(self, auth_service):
        """Test recording failed login attempts."""
        email = "test@example.com"

        await auth_service.record_failed_login(email)
        await auth_service.record_failed_login(email)

        assert len(auth_service.login_attempts[email]) == 2


class TestAuthentication:
    """Test user authentication."""

    @pytest.mark.asyncio
    async def test_authenticate_user_development_mode(self, auth_service):
        """Test user authentication in development mode."""
        auth_service.settings.ENVIRONMENT = "development"

        user = await auth_service.authenticate_user("parent@demo.com", "demo123")

        assert user is not None
        assert user.email == "parent@demo.com"
        assert user.role == "parent"
        assert user.is_active is True

    @pytest.mark.asyncio
    async def test_authenticate_user_invalid_credentials(self, auth_service):
        """Test authentication with invalid credentials."""
        auth_service.settings.ENVIRONMENT = "development"

        user = await auth_service.authenticate_user("parent@demo.com", "wrong_password")

        assert user is None

    @pytest.mark.asyncio
    async def test_authenticate_user_rate_limited(self, auth_service):
        """Test authentication when rate limited."""
        email = "test@example.com"

        # Exceed rate limit
        for _ in range(auth_service.max_login_attempts):
            await auth_service.record_failed_login(email)

        with pytest.raises(HTTPException) as exc_info:
            await auth_service.authenticate_user(email, "password")

        assert exc_info.value.status_code == status.HTTP_429_TOO_MANY_REQUESTS


class TestLoginLogout:
    """Test login and logout functionality."""

    @pytest.mark.asyncio
    async def test_login_success(self, auth_service, mock_redis):
        """Test successful login."""
        auth_service.settings.ENVIRONMENT = "development"
        auth_service.redis_cache = mock_redis

        login_request = LoginRequest(email="parent@demo.com", password="demo123")

        response = await auth_service.login(login_request)

        assert isinstance(response, LoginResponse)
        assert response.access_token is not None
        assert response.refresh_token is not None
        assert response.token_type == "bearer"
        assert response.expires_in == auth_service.access_token_expire_minutes * 60
        assert response.user_info["email"] == "parent@demo.com"

        # Verify session was stored
        mock_redis.setex.assert_called_once()

    @pytest.mark.asyncio
    async def test_login_invalid_credentials(self, auth_service):
        """Test login with invalid credentials."""
        auth_service.settings.ENVIRONMENT = "development"

        login_request = LoginRequest(email="parent@demo.com", password="wrong_password")

        with pytest.raises(HTTPException) as exc_info:
            await auth_service.login(login_request)

        assert exc_info.value.status_code == status.HTTP_401_UNAUTHORIZED
        assert exc_info.value.detail == "Invalid credentials"

    @pytest.mark.asyncio
    async def test_logout_success(self, auth_service, sample_user, mock_redis):
        """Test successful logout."""
        auth_service.redis_cache = mock_redis

        token = auth_service.create_access_token(sample_user)

        success = await auth_service.logout(token)

        assert success is True

        # Verify token was blacklisted
        mock_redis.setex.assert_called()
        # Verify session was deleted
        mock_redis.delete.assert_called_with(f"session:{sample_user['id']}")

    @pytest.mark.asyncio
    async def test_logout_invalid_token(self, auth_service):
        """Test logout with invalid token."""
        success = await auth_service.logout("invalid.token.here")
        assert success is False


class TestTokenRefresh:
    """Test token refresh functionality."""

    @pytest.mark.asyncio
    async def test_refresh_access_token_success(self, auth_service, sample_user):
        """Test successful access token refresh."""
        refresh_token = auth_service.create_refresh_token(sample_user)

        new_access_token = await auth_service.refresh_access_token(refresh_token)

        assert new_access_token is not None
        assert isinstance(new_access_token, str)

        # Verify new token
        payload = await auth_service.verify_token(new_access_token)
        assert payload["sub"] == sample_user["id"]
        assert payload["type"] == "access"

    @pytest.mark.asyncio
    async def test_refresh_access_token_invalid(self, auth_service):
        """Test token refresh with invalid refresh token."""
        new_token = await auth_service.refresh_access_token("invalid.refresh.token")
        assert new_token is None

    @pytest.mark.asyncio
    async def test_refresh_access_token_wrong_type(self, auth_service, sample_user):
        """Test token refresh with access token instead of refresh token."""
        access_token = auth_service.create_access_token(sample_user)

        new_token = await auth_service.refresh_access_token(access_token)
        assert new_token is None
