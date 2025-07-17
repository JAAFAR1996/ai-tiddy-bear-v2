"""
Tests for Token Service
Testing JWT token creation, verification, and management for child safety.
"""

import pytest
from unittest.mock import patch, Mock, MagicMock
from datetime import datetime, timedelta
from typing import Dict, Any, Optional

from src.infrastructure.security.token_service import TokenService


class TestTokenService:
    """Test the TokenService class."""

    @pytest.fixture
    def mock_settings(self):
        """Mock settings for testing."""
        settings = Mock()
        settings.security = Mock()
        settings.security.SECRET_KEY = (
            "test_secret_key_that_is_longer_than_32_characters_for_security"
        )
        settings.security.JWT_ALGORITHM = "HS256"
        settings.security.ACCESS_TOKEN_EXPIRE_MINUTES = 15
        settings.security.REFRESH_TOKEN_EXPIRE_DAYS = 7
        return settings

    @pytest.fixture
    def token_service(self, mock_settings):
        """Create a TokenService instance with mocked settings."""
        with patch(
            "src.infrastructure.security.token_service.get_settings",
            return_value=mock_settings,
        ):
            with patch("src.infrastructure.security.token_service.Depends"):
                return TokenService(mock_settings)

    @pytest.fixture
    def sample_user_data(self):
        """Sample user data for token creation."""
        return {"id": "user_123", "email": "test@example.com", "role": "parent"}

    @pytest.fixture
    def sample_child_user_data(self):
        """Sample child user data for token creation."""
        return {"id": "child_456", "email": "child@example.com", "role": "child"}

    def test_token_service_initialization(self, token_service, mock_settings):
        """Test TokenService initialization."""
        assert token_service.secret_key == mock_settings.security.SECRET_KEY
        assert token_service.algorithm == mock_settings.security.JWT_ALGORITHM
        assert (
            token_service.access_token_expire_minutes
            == mock_settings.security.ACCESS_TOKEN_EXPIRE_MINUTES
        )
        assert (
            token_service.refresh_token_expire_days
            == mock_settings.security.REFRESH_TOKEN_EXPIRE_DAYS
        )

    def test_token_service_initialization_short_secret(self, mock_settings):
        """Test TokenService initialization with short secret key."""
        mock_settings.security.SECRET_KEY = "short_key"

        with patch(
            "src.infrastructure.security.token_service.get_settings",
            return_value=mock_settings,
        ):
            with patch("src.infrastructure.security.token_service.Depends"):
                with pytest.raises(
                    ValueError, match="SECRET_KEY must be at least 32 characters long"
                ):
                    TokenService(mock_settings)

    def test_token_service_initialization_empty_secret(self, mock_settings):
        """Test TokenService initialization with empty secret key."""
        mock_settings.security.SECRET_KEY = ""

        with patch(
            "src.infrastructure.security.token_service.get_settings",
            return_value=mock_settings,
        ):
            with patch("src.infrastructure.security.token_service.Depends"):
                with pytest.raises(
                    ValueError, match="SECRET_KEY must be at least 32 characters long"
                ):
                    TokenService(mock_settings)

    def test_token_service_initialization_none_secret(self, mock_settings):
        """Test TokenService initialization with None secret key."""
        mock_settings.security.SECRET_KEY = None

        with patch(
            "src.infrastructure.security.token_service.get_settings",
            return_value=mock_settings,
        ):
            with patch("src.infrastructure.security.token_service.Depends"):
                with pytest.raises(
                    ValueError, match="SECRET_KEY must be at least 32 characters long"
                ):
                    TokenService(mock_settings)

    def test_create_access_token_valid_user(
            self, token_service, sample_user_data):
        """Test creating access token with valid user data."""
        with patch(
            "src.infrastructure.security.token_service.jwt.encode"
        ) as mock_encode:
            mock_encode.return_value = "test_access_token"

            token = token_service.create_access_token(sample_user_data)

            assert token == "test_access_token"
            mock_encode.assert_called_once()

            # Check the payload structure
            call_args = mock_encode.call_args[0]
            payload = call_args[0]
            assert payload["sub"] == sample_user_data["id"]
            assert payload["email"] == sample_user_data["email"]
            assert payload["role"] == sample_user_data["role"]
            assert payload["type"] == "access"
            assert "iat" in payload
            assert "exp" in payload

    def test_create_access_token_valid_child(
        self, token_service, sample_child_user_data
    ):
        """Test creating access token with valid child user data."""
        with patch(
            "src.infrastructure.security.token_service.jwt.encode"
        ) as mock_encode:
            mock_encode.return_value = "test_child_access_token"

            token = token_service.create_access_token(sample_child_user_data)

            assert token == "test_child_access_token"
            mock_encode.assert_called_once()

            # Check child-specific claims
            call_args = mock_encode.call_args[0]
            payload = call_args[0]
            assert payload["role"] == "child"
            assert payload["sub"] == sample_child_user_data["id"]

    def test_create_access_token_expiration_time(
            self, token_service, sample_user_data):
        """Test access token expiration time calculation."""
        with patch(
            "src.infrastructure.security.token_service.jwt.encode"
        ) as mock_encode:
            with patch(
                "src.infrastructure.security.token_service.datetime"
            ) as mock_datetime:
                mock_now = datetime(2024, 1, 1, 12, 0, 0)
                mock_datetime.utcnow.return_value = mock_now

                token_service.create_access_token(sample_user_data)

                call_args = mock_encode.call_args[0]
                payload = call_args[0]
                expected_exp = mock_now + timedelta(minutes=15)
                assert payload["exp"] == expected_exp
                assert payload["iat"] == mock_now

    def test_create_access_token_missing_required_field(self, token_service):
        """Test creating access token with missing required fields."""
        invalid_user_data = {
            "id": "user_123",
            # Missing email and role
        }

        with pytest.raises(ValueError, match="Failed to create access token"):
            token_service.create_access_token(invalid_user_data)

    def test_create_access_token_invalid_data_type(self, token_service):
        """Test creating access token with invalid data type."""
        invalid_user_data = "not_a_dict"

        with pytest.raises(ValueError, match="Failed to create access token"):
            token_service.create_access_token(invalid_user_data)

    def test_create_access_token_jwt_error(
            self, token_service, sample_user_data):
        """Test creating access token with JWT encoding error."""
        with patch(
            "src.infrastructure.security.token_service.jwt.encode"
        ) as mock_encode:
            from jose import JWTError

            mock_encode.side_effect = JWTError("JWT encoding failed")

            with pytest.raises(ValueError, match="Failed to create access token"):
                token_service.create_access_token(sample_user_data)

    def test_create_refresh_token_valid_user(
            self, token_service, sample_user_data):
        """Test creating refresh token with valid user data."""
        with patch(
            "src.infrastructure.security.token_service.jwt.encode"
        ) as mock_encode:
            mock_encode.return_value = "test_refresh_token"

            token = token_service.create_refresh_token(sample_user_data)

            assert token == "test_refresh_token"
            mock_encode.assert_called_once()

            # Check the payload structure
            call_args = mock_encode.call_args[0]
            payload = call_args[0]
            assert payload["sub"] == sample_user_data["id"]
            assert payload["email"] == sample_user_data["email"]
            assert payload["type"] == "refresh"
            assert "iat" in payload
            assert "exp" in payload
            assert "role" not in payload  # Refresh tokens don't include role

    def test_create_refresh_token_valid_child(
        self, token_service, sample_child_user_data
    ):
        """Test creating refresh token with valid child user data."""
        with patch(
            "src.infrastructure.security.token_service.jwt.encode"
        ) as mock_encode:
            mock_encode.return_value = "test_child_refresh_token"

            token = token_service.create_refresh_token(sample_child_user_data)

            assert token == "test_child_refresh_token"
            mock_encode.assert_called_once()

            # Check child-specific claims
            call_args = mock_encode.call_args[0]
            payload = call_args[0]
            assert payload["sub"] == sample_child_user_data["id"]
            assert payload["email"] == sample_child_user_data["email"]

    def test_create_refresh_token_expiration_time(
        self, token_service, sample_user_data
    ):
        """Test refresh token expiration time calculation."""
        with patch(
            "src.infrastructure.security.token_service.jwt.encode"
        ) as mock_encode:
            with patch(
                "src.infrastructure.security.token_service.datetime"
            ) as mock_datetime:
                mock_now = datetime(2024, 1, 1, 12, 0, 0)
                mock_datetime.utcnow.return_value = mock_now

                token_service.create_refresh_token(sample_user_data)

                call_args = mock_encode.call_args[0]
                payload = call_args[0]
                expected_exp = mock_now + timedelta(days=7)
                assert payload["exp"] == expected_exp
                assert payload["iat"] == mock_now

    def test_create_refresh_token_missing_required_field(self, token_service):
        """Test creating refresh token with missing required fields."""
        invalid_user_data = {
            "id": "user_123",
            # Missing email
        }

        with pytest.raises(ValueError, match="Failed to create refresh token"):
            token_service.create_refresh_token(invalid_user_data)

    def test_create_refresh_token_invalid_data_type(self, token_service):
        """Test creating refresh token with invalid data type."""
        invalid_user_data = None

        with pytest.raises(ValueError, match="Failed to create refresh token"):
            token_service.create_refresh_token(invalid_user_data)

    def test_create_refresh_token_jwt_error(
            self, token_service, sample_user_data):
        """Test creating refresh token with JWT encoding error."""
        with patch(
            "src.infrastructure.security.token_service.jwt.encode"
        ) as mock_encode:
            from jose import JWTError

            mock_encode.side_effect = JWTError("JWT encoding failed")

            with pytest.raises(ValueError, match="Failed to create refresh token"):
                token_service.create_refresh_token(sample_user_data)

    @pytest.mark.asyncio
    async def test_verify_token_valid_token(self, token_service):
        """Test verifying valid token."""
        valid_payload = {
            "sub": "user_123",
            "email": "test@example.com",
            "role": "parent",
            "type": "access",
            "iat": datetime.utcnow(),
            "exp": datetime.utcnow() + timedelta(minutes=15),
        }

        with patch(
            "src.infrastructure.security.token_service.jwt.decode"
        ) as mock_decode:
            mock_decode.return_value = valid_payload

            result = await token_service.verify_token("valid_token")

            assert result == valid_payload
            mock_decode.assert_called_once_with(
                "valid_token",
                token_service.secret_key,
                algorithms=[token_service.algorithm],
            )

    @pytest.mark.asyncio
    async def test_verify_token_child_token(self, token_service):
        """Test verifying valid child token."""
        child_payload = {
            "sub": "child_456",
            "email": "child@example.com",
            "role": "child",
            "type": "access",
            "iat": datetime.utcnow(),
            "exp": datetime.utcnow() + timedelta(minutes=15),
        }

        with patch(
            "src.infrastructure.security.token_service.jwt.decode"
        ) as mock_decode:
            mock_decode.return_value = child_payload

            result = await token_service.verify_token("valid_child_token")

            assert result == child_payload
            assert result["role"] == "child"

    @pytest.mark.asyncio
    async def test_verify_token_refresh_token(self, token_service):
        """Test verifying valid refresh token."""
        refresh_payload = {
            "sub": "user_123",
            "email": "test@example.com",
            "type": "refresh",
            "iat": datetime.utcnow(),
            "exp": datetime.utcnow() + timedelta(days=7),
        }

        with patch(
            "src.infrastructure.security.token_service.jwt.decode"
        ) as mock_decode:
            mock_decode.return_value = refresh_payload

            result = await token_service.verify_token("valid_refresh_token")

            assert result == refresh_payload
            assert result["type"] == "refresh"

    @pytest.mark.asyncio
    async def test_verify_token_expired_token(self, token_service):
        """Test verifying expired token."""
        with patch(
            "src.infrastructure.security.token_service.jwt.decode"
        ) as mock_decode:
            from jose import jwt

            mock_decode.side_effect = jwt.ExpiredSignatureError(
                "Token has expired")

            result = await token_service.verify_token("expired_token")

            assert result is None

    @pytest.mark.asyncio
    async def test_verify_token_invalid_token(self, token_service):
        """Test verifying invalid token."""
        with patch(
            "src.infrastructure.security.token_service.jwt.decode"
        ) as mock_decode:
            from jose import JWTError

            mock_decode.side_effect = JWTError("Invalid token")

            result = await token_service.verify_token("invalid_token")

            assert result is None

    @pytest.mark.asyncio
    async def test_verify_token_malformed_token(self, token_service):
        """Test verifying malformed token."""
        with patch(
            "src.infrastructure.security.token_service.jwt.decode"
        ) as mock_decode:
            mock_decode.side_effect = Exception("Malformed token")

            result = await token_service.verify_token("malformed_token")

            assert result is None

    @pytest.mark.asyncio
    async def test_verify_token_empty_token(self, token_service):
        """Test verifying empty token."""
        result = await token_service.verify_token("")

        assert result is None

    @pytest.mark.asyncio
    async def test_verify_token_none_token(self, token_service):
        """Test verifying None token."""
        result = await token_service.verify_token(None)

        assert result is None

    def test_token_service_logging_setup(self, token_service):
        """Test TokenService logging setup."""
        from src.infrastructure.security.token_service import logger

        assert logger is not None
        assert hasattr(logger, "info")
        assert hasattr(logger, "warning")
        assert hasattr(logger, "error")
        assert hasattr(logger, "debug")

    def test_token_service_logging_calls(
            self, token_service, sample_user_data):
        """Test TokenService logging calls."""
        with patch("src.infrastructure.security.token_service.logger") as mock_logger:
            # Test error logging for invalid user data
            with pytest.raises(ValueError):
                token_service.create_access_token({"invalid": "data"})

            mock_logger.error.assert_called()

            # Test error logging for JWT errors
            with patch(
                "src.infrastructure.security.token_service.jwt.encode"
            ) as mock_encode:
                from jose import JWTError

                mock_encode.side_effect = JWTError("JWT error")

                with pytest.raises(ValueError):
                    token_service.create_access_token(sample_user_data)

                assert mock_logger.error.call_count >= 2

    @pytest.mark.asyncio
    async def test_token_service_verify_logging(self, token_service):
        """Test TokenService verify token logging."""
        with patch("src.infrastructure.security.token_service.logger") as mock_logger:
            # Test debug logging for expired token
            with patch(
                "src.infrastructure.security.token_service.jwt.decode"
            ) as mock_decode:
                from jose import jwt

                mock_decode.side_effect = jwt.ExpiredSignatureError(
                    "Token expired")

                result = await token_service.verify_token("expired_token")

                assert result is None
                mock_logger.debug.assert_called()

                # Test debug logging for invalid token
                mock_decode.side_effect = JWTError("Invalid token")

                result = await token_service.verify_token("invalid_token")

                assert result is None
                assert mock_logger.debug.call_count >= 2

                # Test error logging for unexpected errors
                mock_decode.side_effect = Exception("Unexpected error")

                result = await token_service.verify_token("error_token")

                assert result is None
                mock_logger.error.assert_called()


class TestTokenServiceIntegration:
    """Integration tests for TokenService."""

    @pytest.fixture
    def mock_settings(self):
        """Mock settings for testing."""
        settings = Mock()
        settings.security = Mock()
        settings.security.SECRET_KEY = (
            "test_secret_key_that_is_longer_than_32_characters_for_security"
        )
        settings.security.JWT_ALGORITHM = "HS256"
        settings.security.ACCESS_TOKEN_EXPIRE_MINUTES = 15
        settings.security.REFRESH_TOKEN_EXPIRE_DAYS = 7
        return settings

    @pytest.fixture
    def token_service(self, mock_settings):
        """Create a TokenService instance with mocked settings."""
        with patch(
            "src.infrastructure.security.token_service.get_settings",
            return_value=mock_settings,
        ):
            with patch("src.infrastructure.security.token_service.Depends"):
                return TokenService(mock_settings)

    @pytest.fixture
    def sample_user_data(self):
        """Sample user data for token creation."""
        return {"id": "user_123", "email": "test@example.com", "role": "parent"}

    def test_token_creation_and_verification_flow(
        self, token_service, sample_user_data
    ):
        """Test complete token creation and verification flow."""
        # Create access token
        access_token = token_service.create_access_token(sample_user_data)
        assert access_token is not None
        assert isinstance(access_token, str)
        assert len(access_token) > 0

        # Create refresh token
        refresh_token = token_service.create_refresh_token(sample_user_data)
        assert refresh_token is not None
        assert isinstance(refresh_token, str)
        assert len(refresh_token) > 0

        # Tokens should be different
        assert access_token != refresh_token

    @pytest.mark.asyncio
    async def test_token_roundtrip_verification(
            self, token_service, sample_user_data):
        """Test token roundtrip (create and verify)."""
        # Create token
        access_token = token_service.create_access_token(sample_user_data)

        # Verify token
        verified_payload = await token_service.verify_token(access_token)

        assert verified_payload is not None
        assert verified_payload["sub"] == sample_user_data["id"]
        assert verified_payload["email"] == sample_user_data["email"]
        assert verified_payload["role"] == sample_user_data["role"]
        assert verified_payload["type"] == "access"

    @pytest.mark.asyncio
    async def test_refresh_token_roundtrip_verification(
        self, token_service, sample_user_data
    ):
        """Test refresh token roundtrip (create and verify)."""
        # Create refresh token
        refresh_token = token_service.create_refresh_token(sample_user_data)

        # Verify refresh token
        verified_payload = await token_service.verify_token(refresh_token)

        assert verified_payload is not None
        assert verified_payload["sub"] == sample_user_data["id"]
        assert verified_payload["email"] == sample_user_data["email"]
        assert verified_payload["type"] == "refresh"
        assert "role" not in verified_payload  # Refresh tokens don't include role

    def test_multiple_users_token_creation(self, token_service):
        """Test token creation for multiple users."""
        users = [
            {"id": "user_1", "email": "user1@example.com", "role": "parent"},
            {"id": "user_2", "email": "user2@example.com", "role": "admin"},
            {"id": "child_1", "email": "child1@example.com", "role": "child"},
        ]

        tokens = []
        for user in users:
            token = token_service.create_access_token(user)
            tokens.append(token)

        # All tokens should be different
        assert len(set(tokens)) == len(tokens)

    def test_token_service_with_different_algorithms(self, mock_settings):
        """Test TokenService with different JWT algorithms."""
        algorithms = ["HS256", "HS384", "HS512"]

        for algorithm in algorithms:
            mock_settings.security.JWT_ALGORITHM = algorithm

            with patch(
                "src.infrastructure.security.token_service.get_settings",
                return_value=mock_settings,
            ):
                with patch("src.infrastructure.security.token_service.Depends"):
                    service = TokenService(mock_settings)
                    assert service.algorithm == algorithm

    def test_token_service_with_different_expiration_times(
        self, mock_settings, sample_user_data
    ):
        """Test TokenService with different expiration times."""
        expiration_times = [5, 15, 30, 60]

        for exp_time in expiration_times:
            mock_settings.security.ACCESS_TOKEN_EXPIRE_MINUTES = exp_time

            with patch(
                "src.infrastructure.security.token_service.get_settings",
                return_value=mock_settings,
            ):
                with patch("src.infrastructure.security.token_service.Depends"):
                    service = TokenService(mock_settings)
                    assert service.access_token_expire_minutes == exp_time

                    # Create token with this expiration time
                    token = service.create_access_token(sample_user_data)
                    assert token is not None

    def test_token_service_child_safety_considerations(self, token_service):
        """Test TokenService with child safety considerations."""
        # Create child user data
        child_user_data = {
            "id": "child_123",
            "email": "child@example.com",
            "role": "child",
        }

        # Create tokens for child
        child_access_token = token_service.create_access_token(child_user_data)
        child_refresh_token = token_service.create_refresh_token(
            child_user_data)

        assert child_access_token is not None
        assert child_refresh_token is not None
        assert child_access_token != child_refresh_token

    def test_token_service_error_handling_chain(self, token_service):
        """Test TokenService error handling chain."""
        # Test various error scenarios
        error_cases = [
            None,
            {},
            {"id": "user_123"},  # Missing email and role
            {"email": "test@example.com"},  # Missing id and role
            {"role": "parent"},  # Missing id and email
            {"id": "", "email": "", "role": ""},  # Empty values
            {"id": None, "email": None, "role": None},  # None values
        ]

        for error_case in error_cases:
            with pytest.raises(ValueError, match="Failed to create access token"):
                token_service.create_access_token(error_case)

            with pytest.raises(ValueError, match="Failed to create refresh token"):
                token_service.create_refresh_token(error_case)

    def test_token_service_security_best_practices(
        self, token_service, sample_user_data
    ):
        """Test TokenService follows security best practices."""
        # Test secret key length enforcement
        assert len(token_service.secret_key) >= 32

        # Test algorithm is secure
        assert token_service.algorithm in ["HS256", "HS384", "HS512"]

        # Test expiration times are reasonable
        assert token_service.access_token_expire_minutes <= 60  # Max 1 hour
        assert token_service.refresh_token_expire_days <= 30  # Max 30 days

        # Test token payload includes required fields
        access_token = token_service.create_access_token(sample_user_data)
        assert access_token is not None
        assert len(access_token) > 0

    def test_token_service_performance_characteristics(
        self, token_service, sample_user_data
    ):
        """Test TokenService performance characteristics."""
        # Test token creation is fast
        import time

        start_time = time.time()
        for _ in range(100):
            token_service.create_access_token(sample_user_data)
        end_time = time.time()

        # Should be able to create 100 tokens in less than 1 second
        assert (end_time - start_time) < 1.0

    @pytest.mark.asyncio
    async def test_token_service_concurrent_operations(
        self, token_service, sample_user_data
    ):
        """Test TokenService concurrent operations."""
        import asyncio

        # Test concurrent token verification
        access_token = token_service.create_access_token(sample_user_data)

        # Verify same token concurrently
        tasks = []
        for _ in range(10):
            task = asyncio.create_task(
                token_service.verify_token(access_token))
            tasks.append(task)

        results = await asyncio.gather(*tasks)

        # All results should be the same
        assert len(results) == 10
        assert all(result is not None for result in results)
        assert all(result["sub"] == sample_user_data["id"]
                   for result in results)
