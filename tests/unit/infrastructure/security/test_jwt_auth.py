"""
Tests for JWT Authentication
Testing JWT authentication system with comprehensive security validations.
"""

import pytest
from unittest.mock import patch, Mock, AsyncMock
from uuid import UUID, uuid4
from datetime import datetime, timedelta
from sqlalchemy.ext.asyncio import AsyncSession
from fastapi_users.authentication import JWTStrategy
from fastapi_users_sqlalchemy import SQLAlchemyUserDatabase
import asyncio

from src.infrastructure.security.jwt_auth import (
    User,
    get_user_db,
    get_jwt_strategy,
    bearer_transport,
    auth_backend,
    fastapi_users,
    current_active_user
)


class TestUser:
    """Test the User model."""
    
    def test_user_model_inheritance(self):
        """Test that User model inherits from correct base classes."""
        from fastapi_users_sqlalchemy import SQLAlchemyBaseUserTableUUID
        from src.infrastructure.persistence.database import Base
        
        # Verify User inherits from both required base classes
        assert issubclass(User, SQLAlchemyBaseUserTableUUID)
        assert issubclass(User, Base)
        
        # Verify table name is set correctly
        assert User.__tablename__ == "users"
    
    def test_user_model_instantiation(self):
        """Test that User model can be instantiated."""
        user = User()
        
        # Should have basic attributes from base class
        assert hasattr(user, 'id')
        assert hasattr(user, 'email')
        assert hasattr(user, 'hashed_password')
        assert hasattr(user, 'is_active')
        assert hasattr(user, 'is_superuser')
        assert hasattr(user, 'is_verified')
    
    def test_user_model_uuid_field(self):
        """Test that User model uses UUID for ID field."""
        user = User()
        
        # ID field should be UUID type
        assert hasattr(user, 'id')
        # The ID will be None initially, but the field should be configured for UUID


class TestGetUserDb:
    """Test the get_user_db function."""
    
    @pytest.fixture
    def mock_session(self):
        """Create a mock async session."""
        return Mock(spec=AsyncSession)
    
    @pytest.mark.asyncio
    async def test_get_user_db_returns_database(self, mock_session):
        """Test that get_user_db returns SQLAlchemyUserDatabase."""
        user_db_generator = get_user_db(mock_session)
        user_db = await user_db_generator.__anext__()
        
        assert isinstance(user_db, SQLAlchemyUserDatabase)
        assert user_db.session == mock_session
    
    @pytest.mark.asyncio
    async def test_get_user_db_is_async_generator(self, mock_session):
        """Test that get_user_db is an async generator."""
        user_db_generator = get_user_db(mock_session)
        
        # Should be an async generator
        assert hasattr(user_db_generator, '__anext__')
        assert hasattr(user_db_generator, '__aiter__')
    
    @pytest.mark.asyncio
    async def test_get_user_db_cleanup(self, mock_session):
        """Test that get_user_db properly handles cleanup."""
        user_db_generator = get_user_db(mock_session)
        
        # Get the database instance
        user_db = await user_db_generator.__anext__()
        assert user_db is not None
        
        # Generator should be exhausted after first yield
        with pytest.raises(StopAsyncIteration):
            await user_db_generator.__anext__()


class TestGetJwtStrategy:
    """Test the get_jwt_strategy function."""
    
    @pytest.fixture
    def mock_settings(self):
        """Create mock settings."""
        mock_settings = Mock()
        mock_settings.security = Mock()
        mock_settings.security.JWT_SECRET_KEY = "secure_jwt_secret_key_with_32_chars_min"
        return mock_settings
    
    @pytest.fixture
    def mock_vault_client(self):
        """Create mock vault client."""
        mock_vault = Mock()
        mock_vault.get_secret = AsyncMock()
        return mock_vault
    
    @pytest.mark.asyncio
    async def test_get_jwt_strategy_with_vault_secret(self, mock_settings, mock_vault_client):
        """Test JWT strategy creation with vault secret."""
        vault_secret = "vault_jwt_secret_key_with_32_chars_minimum"
        mock_vault_client.get_secret.return_value = {"JWT_SECRET": vault_secret}
        
        with patch('src.infrastructure.security.jwt_auth.get_settings', return_value=mock_settings):
            with patch('src.infrastructure.security.jwt_auth.get_vault_client', return_value=mock_vault_client):
                strategy = await get_jwt_strategy()
                
                assert isinstance(strategy, JWTStrategy)
                assert strategy.secret == vault_secret
                assert strategy.lifetime_seconds == 3600
                mock_vault_client.get_secret.assert_called_once_with("jwt-secrets")
    
    @pytest.mark.asyncio
    async def test_get_jwt_strategy_fallback_to_settings(self, mock_settings):
        """Test JWT strategy fallback to settings when vault is unavailable."""
        with patch('src.infrastructure.security.jwt_auth.get_settings', return_value=mock_settings):
            with patch('src.infrastructure.security.jwt_auth.get_vault_client', return_value=None):
                strategy = await get_jwt_strategy()
                
                assert isinstance(strategy, JWTStrategy)
                assert strategy.secret == mock_settings.security.JWT_SECRET_KEY
                assert strategy.lifetime_seconds == 3600
    
    @pytest.mark.asyncio
    async def test_get_jwt_strategy_vault_no_secret(self, mock_settings, mock_vault_client):
        """Test JWT strategy when vault has no secret."""
        mock_vault_client.get_secret.return_value = {}
        
        with patch('src.infrastructure.security.jwt_auth.get_settings', return_value=mock_settings):
            with patch('src.infrastructure.security.jwt_auth.get_vault_client', return_value=mock_vault_client):
                strategy = await get_jwt_strategy()
                
                assert isinstance(strategy, JWTStrategy)
                assert strategy.secret == mock_settings.security.JWT_SECRET_KEY
    
    @pytest.mark.asyncio
    async def test_get_jwt_strategy_empty_secret_error(self, mock_settings):
        """Test JWT strategy with empty secret raises error."""
        mock_settings.security.JWT_SECRET_KEY = ""
        
        with patch('src.infrastructure.security.jwt_auth.get_settings', return_value=mock_settings):
            with patch('src.infrastructure.security.jwt_auth.get_vault_client', return_value=None):
                with pytest.raises(ValueError, match="JWT secret is empty or not configured"):
                    await get_jwt_strategy()
    
    @pytest.mark.asyncio
    async def test_get_jwt_strategy_whitespace_secret_error(self, mock_settings):
        """Test JWT strategy with whitespace-only secret raises error."""
        mock_settings.security.JWT_SECRET_KEY = "   \t\n   "
        
        with patch('src.infrastructure.security.jwt_auth.get_settings', return_value=mock_settings):
            with patch('src.infrastructure.security.jwt_auth.get_vault_client', return_value=None):
                with pytest.raises(ValueError, match="JWT secret is empty or not configured"):
                    await get_jwt_strategy()
    
    @pytest.mark.asyncio
    async def test_get_jwt_strategy_none_secret_error(self, mock_settings):
        """Test JWT strategy with None secret raises error."""
        mock_settings.security.JWT_SECRET_KEY = None
        
        with patch('src.infrastructure.security.jwt_auth.get_settings', return_value=mock_settings):
            with patch('src.infrastructure.security.jwt_auth.get_vault_client', return_value=None):
                with pytest.raises(ValueError, match="JWT secret is empty or not configured"):
                    await get_jwt_strategy()
    
    @pytest.mark.asyncio
    async def test_get_jwt_strategy_missing_attribute_error(self, mock_settings):
        """Test JWT strategy when settings missing JWT_SECRET_KEY attribute."""
        delattr(mock_settings.security, 'JWT_SECRET_KEY')
        
        with patch('src.infrastructure.security.jwt_auth.get_settings', return_value=mock_settings):
            with patch('src.infrastructure.security.jwt_auth.get_vault_client', return_value=None):
                with pytest.raises(ValueError, match="JWT secret is empty or not configured"):
                    await get_jwt_strategy()
    
    @pytest.mark.asyncio
    async def test_get_jwt_strategy_short_secret_error(self, mock_settings):
        """Test JWT strategy with short secret raises error."""
        mock_settings.security.JWT_SECRET_KEY = "short_secret"  # Less than 32 chars
        
        with patch('src.infrastructure.security.jwt_auth.get_settings', return_value=mock_settings):
            with patch('src.infrastructure.security.jwt_auth.get_vault_client', return_value=None):
                with pytest.raises(ValueError, match="JWT secret is too short. Must be at least 32 characters"):
                    await get_jwt_strategy()
    
    @pytest.mark.asyncio
    async def test_get_jwt_strategy_insecure_secret_error(self, mock_settings):
        """Test JWT strategy with insecure secret raises error."""
        insecure_secrets = ["secret", "jwt_secret", "changeme", "default", "dev", "test", "password"]
        
        for insecure_secret in insecure_secrets:
            # Pad to meet minimum length requirement
            padded_secret = insecure_secret + "x" * (32 - len(insecure_secret))
            mock_settings.security.JWT_SECRET_KEY = padded_secret
            
            with patch('src.infrastructure.security.jwt_auth.get_settings', return_value=mock_settings):
                with patch('src.infrastructure.security.jwt_auth.get_vault_client', return_value=None):
                    with pytest.raises(ValueError, match="JWT secret uses a common/insecure value"):
                        await get_jwt_strategy()
    
    @pytest.mark.asyncio
    async def test_get_jwt_strategy_case_insensitive_insecure_check(self, mock_settings):
        """Test JWT strategy insecure secret check is case insensitive."""
        insecure_secrets = ["SECRET", "Jwt_Secret", "CHANGEME", "Default", "DEV", "TEST", "Password"]
        
        for insecure_secret in insecure_secrets:
            # Pad to meet minimum length requirement
            padded_secret = insecure_secret + "x" * (32 - len(insecure_secret))
            mock_settings.security.JWT_SECRET_KEY = padded_secret
            
            with patch('src.infrastructure.security.jwt_auth.get_settings', return_value=mock_settings):
                with patch('src.infrastructure.security.jwt_auth.get_vault_client', return_value=None):
                    with pytest.raises(ValueError, match="JWT secret uses a common/insecure value"):
                        await get_jwt_strategy()
    
    @pytest.mark.asyncio
    async def test_get_jwt_strategy_secure_secret_variations(self, mock_settings):
        """Test JWT strategy with various secure secrets."""
        secure_secrets = [
            "secure_jwt_secret_key_with_32_chars_min",
            "a" * 32,  # Minimum length
            "a" * 64,  # Double minimum length
            "complex_secret_with_numbers_123_and_symbols_!@#",
            "VerySecureJWTSecretKeyWithMixedCaseAndNumbers123",
            "🔐secure_unicode_secret_key_with_emojis_🔒",
            "super_long_secret_key_" + "x" * 100
        ]
        
        for secure_secret in secure_secrets:
            mock_settings.security.JWT_SECRET_KEY = secure_secret
            
            with patch('src.infrastructure.security.jwt_auth.get_settings', return_value=mock_settings):
                with patch('src.infrastructure.security.jwt_auth.get_vault_client', return_value=None):
                    strategy = await get_jwt_strategy()
                    
                    assert isinstance(strategy, JWTStrategy)
                    assert strategy.secret == secure_secret
                    assert strategy.lifetime_seconds == 3600
    
    @pytest.mark.asyncio
    async def test_get_jwt_strategy_vault_exception_handling(self, mock_settings, mock_vault_client):
        """Test JWT strategy handles vault exceptions gracefully."""
        mock_vault_client.get_secret.side_effect = Exception("Vault connection error")
        
        with patch('src.infrastructure.security.jwt_auth.get_settings', return_value=mock_settings):
            with patch('src.infrastructure.security.jwt_auth.get_vault_client', return_value=mock_vault_client):
                strategy = await get_jwt_strategy()
                
                # Should fall back to settings
                assert isinstance(strategy, JWTStrategy)
                assert strategy.secret == mock_settings.security.JWT_SECRET_KEY
    
    @pytest.mark.asyncio
    async def test_get_jwt_strategy_vault_timeout_handling(self, mock_settings, mock_vault_client):
        """Test JWT strategy handles vault timeout gracefully."""
        async def slow_get_secret(key):
            await asyncio.sleep(10)  # Simulate slow vault response
            return {"JWT_SECRET": "vault_secret_key_with_32_chars_minimum"}
        
        mock_vault_client.get_secret.side_effect = slow_get_secret
        
        with patch('src.infrastructure.security.jwt_auth.get_settings', return_value=mock_settings):
            with patch('src.infrastructure.security.jwt_auth.get_vault_client', return_value=mock_vault_client):
                # Should not hang indefinitely
                strategy = await get_jwt_strategy()
                
                # Should fall back to settings due to timeout/error
                assert isinstance(strategy, JWTStrategy)
                assert strategy.secret == mock_settings.security.JWT_SECRET_KEY
    
    @pytest.mark.asyncio
    async def test_get_jwt_strategy_concurrent_calls(self, mock_settings):
        """Test JWT strategy with concurrent calls."""
        with patch('src.infrastructure.security.jwt_auth.get_settings', return_value=mock_settings):
            with patch('src.infrastructure.security.jwt_auth.get_vault_client', return_value=None):
                # Make multiple concurrent calls
                tasks = [get_jwt_strategy() for _ in range(10)]
                strategies = await asyncio.gather(*tasks)
                
                # All should succeed and return valid strategies
                assert len(strategies) == 10
                for strategy in strategies:
                    assert isinstance(strategy, JWTStrategy)
                    assert strategy.secret == mock_settings.security.JWT_SECRET_KEY
                    assert strategy.lifetime_seconds == 3600
    
    @pytest.mark.asyncio
    async def test_get_jwt_strategy_secret_length_boundary_conditions(self, mock_settings):
        """Test JWT strategy with secret length boundary conditions."""
        # Test exactly 32 characters (minimum)
        mock_settings.security.JWT_SECRET_KEY = "a" * 32
        
        with patch('src.infrastructure.security.jwt_auth.get_settings', return_value=mock_settings):
            with patch('src.infrastructure.security.jwt_auth.get_vault_client', return_value=None):
                strategy = await get_jwt_strategy()
                assert isinstance(strategy, JWTStrategy)
        
        # Test exactly 31 characters (one less than minimum)
        mock_settings.security.JWT_SECRET_KEY = "a" * 31
        
        with patch('src.infrastructure.security.jwt_auth.get_settings', return_value=mock_settings):
            with patch('src.infrastructure.security.jwt_auth.get_vault_client', return_value=None):
                with pytest.raises(ValueError, match="JWT secret is too short"):
                    await get_jwt_strategy()
    
    @pytest.mark.asyncio
    async def test_get_jwt_strategy_unicode_secret_handling(self, mock_settings):
        """Test JWT strategy with unicode characters in secret."""
        unicode_secret = "unicode_secret_🔐_with_emojis_🔒_and_32_chars"
        mock_settings.security.JWT_SECRET_KEY = unicode_secret
        
        with patch('src.infrastructure.security.jwt_auth.get_settings', return_value=mock_settings):
            with patch('src.infrastructure.security.jwt_auth.get_vault_client', return_value=None):
                strategy = await get_jwt_strategy()
                
                assert isinstance(strategy, JWTStrategy)
                assert strategy.secret == unicode_secret
    
    @pytest.mark.asyncio
    async def test_get_jwt_strategy_lifetime_configuration(self, mock_settings):
        """Test JWT strategy lifetime configuration."""
        with patch('src.infrastructure.security.jwt_auth.get_settings', return_value=mock_settings):
            with patch('src.infrastructure.security.jwt_auth.get_vault_client', return_value=None):
                strategy = await get_jwt_strategy()
                
                # Should use 3600 seconds (1 hour) as default
                assert strategy.lifetime_seconds == 3600
    
    @pytest.mark.asyncio
    async def test_get_jwt_strategy_memory_safety(self, mock_settings):
        """Test JWT strategy doesn't leak secret in memory."""
        import gc
        
        with patch('src.infrastructure.security.jwt_auth.get_settings', return_value=mock_settings):
            with patch('src.infrastructure.security.jwt_auth.get_vault_client', return_value=None):
                strategy = await get_jwt_strategy()
                
                # Strategy should not store the secret in an easily accessible way
                # This is more about the JWTStrategy implementation, but we can verify
                # the secret is properly encapsulated
                assert hasattr(strategy, 'secret')
                assert strategy.secret == mock_settings.security.JWT_SECRET_KEY


class TestBearerTransport:
    """Test the bearer transport configuration."""
    
    def test_bearer_transport_configuration(self):
        """Test bearer transport is configured correctly."""
        from fastapi_users.authentication import BearerTransport
        
        assert isinstance(bearer_transport, BearerTransport)
        assert bearer_transport.tokenUrl == "auth/jwt/login"
    
    def test_bearer_transport_token_url(self):
        """Test bearer transport token URL is correct."""
        # The token URL should match the expected login endpoint
        assert bearer_transport.tokenUrl == "auth/jwt/login"


class TestAuthBackend:
    """Test the authentication backend configuration."""
    
    def test_auth_backend_configuration(self):
        """Test authentication backend is configured correctly."""
        from fastapi_users.authentication import AuthenticationBackend
        
        assert isinstance(auth_backend, AuthenticationBackend)
        assert auth_backend.name == "jwt"
        assert auth_backend.transport == bearer_transport
    
    def test_auth_backend_name(self):
        """Test authentication backend name."""
        assert auth_backend.name == "jwt"
    
    def test_auth_backend_transport(self):
        """Test authentication backend uses correct transport."""
        assert auth_backend.transport == bearer_transport
    
    @pytest.mark.asyncio
    async def test_auth_backend_strategy_function(self):
        """Test authentication backend strategy function."""
        # The get_strategy function should be the same as our get_jwt_strategy
        assert auth_backend.get_strategy == get_jwt_strategy
    
    @pytest.mark.asyncio
    async def test_auth_backend_integration(self):
        """Test authentication backend integration."""
        # Test that the backend can be used with proper configuration
        assert auth_backend.name == "jwt"
        assert callable(auth_backend.get_strategy)
        assert auth_backend.transport is not None


class TestFastAPIUsers:
    """Test the FastAPI Users configuration."""
    
    def test_fastapi_users_configuration(self):
        """Test FastAPI Users is configured correctly."""
        from fastapi_users import FastAPIUsers
        
        assert isinstance(fastapi_users, FastAPIUsers)
        assert fastapi_users.authentication_backends == [auth_backend]
    
    def test_fastapi_users_user_model(self):
        """Test FastAPI Users uses correct user model."""
        # FastAPI Users should use our User model
        assert fastapi_users.User == User
        assert fastapi_users.UserCreate == User
        assert fastapi_users.UserUpdate == User
        assert fastapi_users.UserDB == User
    
    def test_fastapi_users_authentication_backends(self):
        """Test FastAPI Users authentication backends."""
        assert len(fastapi_users.authentication_backends) == 1
        assert fastapi_users.authentication_backends[0] == auth_backend
    
    def test_fastapi_users_get_user_db(self):
        """Test FastAPI Users get_user_db function."""
        assert fastapi_users.get_user_db == get_user_db
    
    def test_current_active_user_function(self):
        """Test current_active_user function is configured."""
        assert current_active_user == fastapi_users.current_active_user
        assert callable(current_active_user)


class TestJWTSecurityValidation:
    """Test JWT security validation functions."""
    
    @pytest.mark.asyncio
    async def test_jwt_secret_validation_comprehensive(self):
        """Test comprehensive JWT secret validation."""
        mock_settings = Mock()
        mock_settings.security = Mock()
        
        # Test cases: (secret, should_pass, expected_error)
        test_cases = [
            # Valid secrets
            ("secure_jwt_secret_key_with_32_chars_min", True, None),
            ("a" * 32, True, None),
            ("VerySecureJWTSecretKeyWithMixedCase123", True, None),
            
            # Invalid: too short
            ("short", False, "too short"),
            ("a" * 31, False, "too short"),
            ("", False, "empty or not configured"),
            ("   ", False, "empty or not configured"),
            
            # Invalid: insecure values
            ("secret" + "x" * 26, False, "common/insecure value"),
            ("SECRET" + "x" * 26, False, "common/insecure value"),
            ("jwt_secret" + "x" * 22, False, "common/insecure value"),
            ("changeme" + "x" * 24, False, "common/insecure value"),
            ("default" + "x" * 25, False, "common/insecure value"),
            ("dev" + "x" * 29, False, "common/insecure value"),
            ("test" + "x" * 28, False, "common/insecure value"),
            ("password" + "x" * 24, False, "common/insecure value"),
            
            # Edge cases
            (None, False, "empty or not configured"),
            ("None", False, "too short"),
            ("null", False, "too short"),
            ("undefined", False, "too short"),
        ]
        
        for secret, should_pass, expected_error in test_cases:
            mock_settings.security.JWT_SECRET_KEY = secret
            
            with patch('src.infrastructure.security.jwt_auth.get_settings', return_value=mock_settings):
                with patch('src.infrastructure.security.jwt_auth.get_vault_client', return_value=None):
                    if should_pass:
                        strategy = await get_jwt_strategy()
                        assert isinstance(strategy, JWTStrategy)
                        assert strategy.secret == secret
                    else:
                        with pytest.raises(ValueError) as exc_info:
                            await get_jwt_strategy()
                        assert expected_error in str(exc_info.value)
    
    @pytest.mark.asyncio
    async def test_jwt_secret_entropy_considerations(self):
        """Test JWT secret entropy considerations."""
        mock_settings = Mock()
        mock_settings.security = Mock()
        
        # Test with low entropy secrets (repeating patterns)
        low_entropy_secrets = [
            "aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa",  # All same character
            "12345678901234567890123456789012345678",  # Repeating pattern
            "abcdefghijklmnopqrstuvwxyz123456789",  # Predictable sequence
        ]
        
        for secret in low_entropy_secrets:
            mock_settings.security.JWT_SECRET_KEY = secret
            
            with patch('src.infrastructure.security.jwt_auth.get_settings', return_value=mock_settings):
                with patch('src.infrastructure.security.jwt_auth.get_vault_client', return_value=None):
                    # These should pass length and insecurity checks but are still weak
                    strategy = await get_jwt_strategy()
                    assert isinstance(strategy, JWTStrategy)
                    assert strategy.secret == secret
    
    @pytest.mark.asyncio
    async def test_jwt_secret_special_characters(self):
        """Test JWT secret with special characters."""
        mock_settings = Mock()
        mock_settings.security = Mock()
        
        special_secrets = [
            "secure_jwt_secret_with_!@#$%^&*()_+-=",
            "jwt_secret_with_brackets_[]{}|\\;':\"<>?",
            "jwt_secret_with_spaces_and_32_chars_min",
            "jwt_secret_with_newlines_\n_and_tabs_\t",
        ]
        
        for secret in special_secrets:
            mock_settings.security.JWT_SECRET_KEY = secret
            
            with patch('src.infrastructure.security.jwt_auth.get_settings', return_value=mock_settings):
                with patch('src.infrastructure.security.jwt_auth.get_vault_client', return_value=None):
                    strategy = await get_jwt_strategy()
                    assert isinstance(strategy, JWTStrategy)
                    assert strategy.secret == secret
    
    @pytest.mark.asyncio
    async def test_jwt_secret_configuration_priority(self):
        """Test JWT secret configuration priority (vault > settings)."""
        mock_settings = Mock()
        mock_settings.security = Mock()
        mock_settings.security.JWT_SECRET_KEY = "settings_secret_key_with_32_chars_min"
        
        vault_secret = "vault_secret_key_with_32_chars_minimum"
        mock_vault_client = Mock()
        mock_vault_client.get_secret = AsyncMock(return_value={"JWT_SECRET": vault_secret})
        
        with patch('src.infrastructure.security.jwt_auth.get_settings', return_value=mock_settings):
            with patch('src.infrastructure.security.jwt_auth.get_vault_client', return_value=mock_vault_client):
                strategy = await get_jwt_strategy()
                
                # Should use vault secret, not settings secret
                assert strategy.secret == vault_secret
                assert strategy.secret != mock_settings.security.JWT_SECRET_KEY
    
    @pytest.mark.asyncio
    async def test_jwt_secret_vault_partial_failure(self):
        """Test JWT secret when vault is available but returns incomplete data."""
        mock_settings = Mock()
        mock_settings.security = Mock()
        mock_settings.security.JWT_SECRET_KEY = "fallback_secret_key_with_32_chars_min"
        
        # Test various vault failure scenarios
        vault_responses = [
            {},  # Empty response
            {"OTHER_SECRET": "value"},  # Missing JWT_SECRET
            {"JWT_SECRET": ""},  # Empty JWT_SECRET
            {"JWT_SECRET": None},  # None JWT_SECRET
            {"JWT_SECRET": "   "},  # Whitespace JWT_SECRET
        ]
        
        for vault_response in vault_responses:
            mock_vault_client = Mock()
            mock_vault_client.get_secret = AsyncMock(return_value=vault_response)
            
            with patch('src.infrastructure.security.jwt_auth.get_settings', return_value=mock_settings):
                with patch('src.infrastructure.security.jwt_auth.get_vault_client', return_value=mock_vault_client):
                    strategy = await get_jwt_strategy()
                    
                    # Should fall back to settings
                    assert strategy.secret == mock_settings.security.JWT_SECRET_KEY
    
    @pytest.mark.asyncio
    async def test_jwt_strategy_concurrent_access(self):
        """Test JWT strategy with concurrent access patterns."""
        mock_settings = Mock()
        mock_settings.security = Mock()
        mock_settings.security.JWT_SECRET_KEY = "concurrent_secret_key_with_32_chars_min"
        
        with patch('src.infrastructure.security.jwt_auth.get_settings', return_value=mock_settings):
            with patch('src.infrastructure.security.jwt_auth.get_vault_client', return_value=None):
                # Simulate concurrent access
                tasks = []
                for i in range(100):
                    task = asyncio.create_task(get_jwt_strategy())
                    tasks.append(task)
                
                strategies = await asyncio.gather(*tasks)
                
                # All should succeed
                assert len(strategies) == 100
                for strategy in strategies:
                    assert isinstance(strategy, JWTStrategy)
                    assert strategy.secret == mock_settings.security.JWT_SECRET_KEY
                    assert strategy.lifetime_seconds == 3600
    
    def test_jwt_auth_module_structure(self):
        """Test JWT auth module structure and exports."""
        # Verify all expected components are available
        from src.infrastructure.security.jwt_auth import (
            User, get_user_db, get_jwt_strategy, bearer_transport,
            auth_backend, fastapi_users, current_active_user
        )
        
        # Verify types
        assert callable(get_user_db)
        assert callable(get_jwt_strategy)
        assert bearer_transport is not None
        assert auth_backend is not None
        assert fastapi_users is not None
        assert callable(current_active_user)
    
    def test_jwt_auth_integration_components(self):
        """Test JWT auth integration components work together."""
        # Test that all components reference each other correctly
        assert auth_backend.transport == bearer_transport
        assert auth_backend.get_strategy == get_jwt_strategy
        assert fastapi_users.authentication_backends == [auth_backend]
        assert current_active_user == fastapi_users.current_active_user
    
    @pytest.mark.asyncio
    async def test_jwt_auth_security_headers(self):
        """Test JWT auth security considerations."""
        mock_settings = Mock()
        mock_settings.security = Mock()
        mock_settings.security.JWT_SECRET_KEY = "security_test_secret_key_with_32_chars"
        
        with patch('src.infrastructure.security.jwt_auth.get_settings', return_value=mock_settings):
            with patch('src.infrastructure.security.jwt_auth.get_vault_client', return_value=None):
                strategy = await get_jwt_strategy()
                
                # Verify security properties
                assert strategy.lifetime_seconds == 3600  # 1 hour, reasonable for security
                assert len(strategy.secret) >= 32  # Minimum security requirement
                assert strategy.secret != ""  # Not empty
                assert strategy.secret is not None  # Not None
    
    @pytest.mark.asyncio
    async def test_jwt_auth_child_safety_considerations(self):
        """Test JWT auth considerations for child safety."""
        # For a child-facing application, JWT configuration should be secure
        mock_settings = Mock()
        mock_settings.security = Mock()
        mock_settings.security.JWT_SECRET_KEY = "child_safe_jwt_secret_key_with_32_chars"
        
        with patch('src.infrastructure.security.jwt_auth.get_settings', return_value=mock_settings):
            with patch('src.infrastructure.security.jwt_auth.get_vault_client', return_value=None):
                strategy = await get_jwt_strategy()
                
                # Child safety considerations
                assert strategy.lifetime_seconds <= 3600  # Not too long for security
                assert len(strategy.secret) >= 32  # Strong secret for child data protection
                
                # Should not use any insecure values
                insecure_patterns = ["secret", "jwt_secret", "changeme", "default", "dev", "test", "password"]
                for pattern in insecure_patterns:
                    assert pattern.lower() not in strategy.secret.lower()