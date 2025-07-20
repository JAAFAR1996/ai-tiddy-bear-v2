try:
from domain.value_objects.safety_level import SafetyLevel
from infrastructure.security.safety_monitor_service import SafetyMonitorService
from infrastructure.security.vault_client import VaultClient
from infrastructure.security.security_manager import SecurityManager
from infrastructure.security.rate_limiter import RateLimiter
from infrastructure.security.jwt_auth import JWTAuth, JWTTokenData
import jwt
from datetime import datetime, timedelta
from unittest.mock import Mock, patch, AsyncMock
from fastapi_users import BaseUserManager, FastAPIUsers
except ImportError:
    # Mock fastapi_users
    class BaseUserManager:
        def __init__(self, *args, **kwargs):
            pass

    class FastAPIUsers:
        def __init__(self, *args, **kwargs):
            pass


import sys
from pathlib import Path

# Add src to path
src_path = Path(__file__).parent
while src_path.name != "backend" and src_path.parent != src_path:
    src_path = src_path.parent
src_path = src_path / "src"

if str(src_path) not in sys.path:
    sys.path.insert(0, str(src_path))

"""Tests for security components."""

try:
    import pytest
except ImportError:
    try:
        from common.mock_pytest import pytest
    except ImportError:
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


class TestJWTAuth:
    """Test JWT authentication functionality."""

    @pytest.fixture
    def jwt_auth(self):
        """Create JWT auth instance."""
        return JWTAuth(
            secret_key="test-secret-key",
            algorithm="HS256",
            access_token_expire_minutes=30,
        )

    def test_create_access_token(self, jwt_auth):
        """Test creating access token."""
        data = {"sub": "parent123", "role": "parent"}
        token = jwt_auth.create_access_token(data)

        assert isinstance(token, str)
        assert len(token) > 0

        # Decode and verify
        decoded = jwt.decode(token, "test-secret-key", algorithms=["HS256"])
        assert decoded["sub"] == "parent123"
        assert decoded["role"] == "parent"
        assert "exp" in decoded

    def test_create_access_token_with_expiration(self, jwt_auth):
        """Test creating token with custom expiration."""
        data = {"sub": "parent123"}
        expires_delta = timedelta(minutes=60)

        token = jwt_auth.create_access_token(data, expires_delta)
        decoded = jwt.decode(token, "test-secret-key", algorithms=["HS256"])

        exp_time = datetime.fromtimestamp(decoded["exp"])
        expected_time = datetime.utcnow() + expires_delta

        # Allow 5 second tolerance
        assert abs((exp_time - expected_time).total_seconds()) < 5

    def test_verify_token_valid(self, jwt_auth):
        """Test verifying valid token."""
        data = {
            "sub": "parent123",
            "role": "parent",
            "permissions": [
                "read",
                "write"]}
        token = jwt_auth.create_access_token(data)

        token_data = jwt_auth.verify_token(token)

        assert isinstance(token_data, JWTTokenData)
        assert token_data.subject == "parent123"
        assert token_data.role == "parent"
        assert "read" in token_data.permissions
        assert "write" in token_data.permissions

    def test_verify_token_expired(self, jwt_auth):
        """Test verifying expired token."""
        data = {"sub": "parent123"}
        expires_delta = timedelta(seconds=-1)  # Already expired

        token = jwt_auth.create_access_token(data, expires_delta)

        with pytest.raises(jwt.ExpiredSignatureError):
            jwt_auth.verify_token(token)

    def test_verify_token_invalid_signature(self, jwt_auth):
        """Test verifying token with invalid signature."""
        # Create token with different secret
        data = {"sub": "parent123"}
        token = jwt.encode(data, "wrong-secret", algorithm="HS256")

        with pytest.raises(jwt.InvalidSignatureError):
            jwt_auth.verify_token(token)

    def test_verify_token_invalid_format(self, jwt_auth):
        """Test verifying malformed token."""
        invalid_token = "invalid.token.format"

        with pytest.raises(jwt.DecodeError):
            jwt_auth.verify_token(invalid_token)

    def test_refresh_token(self, jwt_auth):
        """Test refreshing token."""
        data = {"sub": "parent123", "role": "parent"}
        original_token = jwt_auth.create_access_token(data)

        # Wait a moment to ensure different timestamps
        import time

        time.sleep(0.1)

        new_token = jwt_auth.refresh_token(original_token)

        assert new_token != original_token

        # Verify new token is valid
        new_token_data = jwt_auth.verify_token(new_token)
        assert new_token_data.subject == "parent123"
        assert new_token_data.role == "parent"

    def test_token_data_permissions(self):
        """Test JWTTokenData permission handling."""
        token_data = JWTTokenData(
            subject="parent123", role="parent", permissions=["read", "write", "admin"]
        )

        assert token_data.has_permission("read")
        assert token_data.has_permission("write")
        assert token_data.has_permission("admin")
        assert not token_data.has_permission("delete")

    def test_token_data_role_check(self):
        """Test JWTTokenData role checking."""
        parent_token = JWTTokenData(
            subject="parent123", role="parent", permissions=["read", "write"]
        )

        admin_token = JWTTokenData(
            subject="admin456",
            role="admin",
            permissions=["read", "write", "admin", "delete"],
        )

        assert parent_token.is_parent()
        assert not parent_token.is_admin()
        assert admin_token.is_admin()
        assert not admin_token.is_parent()


class TestRateLimiter:
    """Test rate limiting functionality."""

    @pytest.fixture
    def rate_limiter(self):
        """Create rate limiter instance."""
        return RateLimiter(
            max_requests=10, time_window=60, storage_backend="memory"  # 60 seconds
        )

    @pytest.mark.asyncio
    async def test_allow_request_within_limit(self, rate_limiter):
        """Test allowing request within rate limit."""
        user_id = "user123"

        # First request should be allowed
        allowed = await rate_limiter.is_allowed(user_id)
        assert allowed is True

        # Record the request
        await rate_limiter.record_request(user_id)

    @pytest.mark.asyncio
    async def test_block_request_exceeding_limit(self, rate_limiter):
        """Test blocking request that exceeds rate limit."""
        user_id = "user456"

        # Make maximum allowed requests
        for i in range(10):
            allowed = await rate_limiter.is_allowed(user_id)
            assert allowed is True
            await rate_limiter.record_request(user_id)

        # Next request should be blocked
        allowed = await rate_limiter.is_allowed(user_id)
        assert allowed is False

    @pytest.mark.asyncio
    async def test_rate_limit_reset_after_window(self, rate_limiter):
        """Test rate limit reset after time window."""
        user_id = "user789"

        # Mock time to simulate window expiration
        with patch("time.time") as mock_time:
            # Start at time 0
            mock_time.return_value = 0

            # Fill up the rate limit
            for i in range(10):
                await rate_limiter.record_request(user_id)

            # Should be blocked
            allowed = await rate_limiter.is_allowed(user_id)
            assert allowed is False

            # Move time forward past window
            mock_time.return_value = 61  # Past 60 second window

            # Should be allowed again
            allowed = await rate_limiter.is_allowed(user_id)
            assert allowed is True

    @pytest.mark.asyncio
    async def test_different_users_separate_limits(self, rate_limiter):
        """Test that different users have separate rate limits."""
        user1 = "user1"
        user2 = "user2"

        # Fill rate limit for user1
        for i in range(10):
            await rate_limiter.record_request(user1)

        # User1 should be blocked
        allowed1 = await rate_limiter.is_allowed(user1)
        assert allowed1 is False

        # User2 should still be allowed
        allowed2 = await rate_limiter.is_allowed(user2)
        assert allowed2 is True

    @pytest.mark.asyncio
    async def test_get_remaining_requests(self, rate_limiter):
        """Test getting remaining requests count."""
        user_id = "user_remaining"

        # Initially should have full limit
        remaining = await rate_limiter.get_remaining_requests(user_id)
        assert remaining == 10

        # After some requests, should decrease
        await rate_limiter.record_request(user_id)
        await rate_limiter.record_request(user_id)
        await rate_limiter.record_request(user_id)

        remaining = await rate_limiter.get_remaining_requests(user_id)
        assert remaining == 7

    @pytest.mark.asyncio
    async def test_rate_limit_headers(self, rate_limiter):
        """Test rate limit headers for API responses."""
        user_id = "user_headers"

        headers = await rate_limiter.get_rate_limit_headers(user_id)

        assert "X-RateLimit-Limit" in headers
        assert "X-RateLimit-Remaining" in headers
        assert "X-RateLimit-Reset" in headers

        assert headers["X-RateLimit-Limit"] == "10"
        assert int(headers["X-RateLimit-Remaining"]) <= 10


class TestSecurityManager:
    """Test security manager functionality."""

    @pytest.fixture
    def security_manager(self):
        """Create security manager instance."""
        return SecurityManager(
            jwt_auth=Mock(spec=JWTAuth),
            rate_limiter=Mock(spec=RateLimiter),
            vault_client=Mock(spec=VaultClient),
        )

    @pytest.mark.asyncio
    async def test_authenticate_user_success(self, security_manager):
        """Test successful user authentication."""
        # Mock JWT auth
        token_data = JWTTokenData(
            subject="parent123", role="parent", permissions=["read", "write"]
        )
        security_manager.jwt_auth.verify_token.return_value = token_data

        # Mock rate limiting
        security_manager.rate_limiter.is_allowed.return_value = True

        token = "valid.jwt.token"
        user_data = await security_manager.authenticate_user(token)

        assert user_data == token_data
        security_manager.jwt_auth.verify_token.assert_called_once_with(token)

    @pytest.mark.asyncio
    async def test_authenticate_user_rate_limited(self, security_manager):
        """Test authentication with rate limiting."""
        # Mock rate limiting as blocked
        security_manager.rate_limiter.is_allowed.return_value = False

        token = "valid.jwt.token"

        with pytest.raises(Exception) as exc_info:
            await security_manager.authenticate_user(token)

        assert "rate limit" in str(exc_info.value).lower()

    @pytest.mark.asyncio
    async def test_authenticate_user_invalid_token(self, security_manager):
        """Test authentication with invalid token."""
        # Mock JWT auth to raise exception
        security_manager.jwt_auth.verify_token.side_effect = jwt.InvalidTokenError(
            "Invalid token"
        )
        security_manager.rate_limiter.is_allowed.return_value = True

        token = "invalid.jwt.token"

        with pytest.raises(jwt.InvalidTokenError):
            await security_manager.authenticate_user(token)

    @pytest.mark.asyncio
    async def test_authorize_action_success(self, security_manager):
        """Test successful action authorization."""
        token_data = JWTTokenData(
            subject="parent123",
            role="parent",
            permissions=["read", "write", "child_management"],
        )

        required_permission = "child_management"
        authorized = await security_manager.authorize_action(
            token_data, required_permission
        )

        assert authorized is True

    @pytest.mark.asyncio
    async def test_authorize_action_insufficient_permissions(
            self, security_manager):
        """Test authorization with insufficient permissions."""
        token_data = JWTTokenData(
            subject="parent123", role="parent", permissions=["read"]
        )

        required_permission = "admin"
        authorized = await security_manager.authorize_action(
            token_data, required_permission
        )

        assert authorized is False

    @pytest.mark.asyncio
    async def test_encrypt_sensitive_data(self, security_manager):
        """Test encrypting sensitive data."""
        # Mock vault client
        security_manager.vault_client.encrypt.return_value = "encrypted_data"

        sensitive_data = "child_profile_data"
        encrypted = await security_manager.encrypt_sensitive_data(sensitive_data)

        assert encrypted == "encrypted_data"
        security_manager.vault_client.encrypt.assert_called_once_with(
            sensitive_data)

    @pytest.mark.asyncio
    async def test_decrypt_sensitive_data(self, security_manager):
        """Test decrypting sensitive data."""
        # Mock vault client
        security_manager.vault_client.decrypt.return_value = "decrypted_data"

        encrypted_data = "encrypted_data"
        decrypted = await security_manager.decrypt_sensitive_data(encrypted_data)

        assert decrypted == "decrypted_data"
        security_manager.vault_client.decrypt.assert_called_once_with(
            encrypted_data)


class TestSafetyMonitorService:
    """Test safety monitoring functionality."""

    @pytest.fixture
    def safety_monitor(self):
        """Create safety monitor service."""
        return SafetyMonitorService(
            toxicity_threshold=0.7,
            bias_threshold=0.6,
            content_filters=["violence", "inappropriate", "adult_content"],
        )

    @pytest.mark.asyncio
    async def test_analyze_content_safe(self, safety_monitor):
        """Test analyzing safe content."""
        safe_content = "Hello! Would you like to hear a story about friendly animals?"

        result = await safety_monitor.analyze_content(safe_content)

        assert result.is_safe is True
        assert result.safety_level == SafetyLevel.SAFE
        assert result.toxicity_score < 0.3
        assert result.confidence > 0.8

    @pytest.mark.asyncio
    async def test_analyze_content_toxic(self, safety_monitor):
        """Test analyzing toxic content."""
        toxic_content = (
            "This content contains harmful and inappropriate language for children."
        )

        # Mock the toxicity detection
        with patch.object(safety_monitor, "_detect_toxicity") as mock_detect:
            mock_detect.return_value = 0.9  # High toxicity

            result = await safety_monitor.analyze_content(toxic_content)

            assert result.is_safe is False
            assert result.safety_level in [
                SafetyLevel.WARNING, SafetyLevel.CRITICAL]
            assert result.toxicity_score > 0.7

    @pytest.mark.asyncio
    async def test_analyze_content_bias_detection(self, safety_monitor):
        """Test bias detection in content."""
        biased_content = (
            "Content that might contain subtle bias against certain groups."
        )

        # Mock bias detection
        with patch.object(safety_monitor, "_detect_bias") as mock_bias:
            mock_bias.return_value = {
                "gender_bias": 0.8,
                "racial_bias": 0.2,
                "age_bias": 0.1,
            }

            result = await safety_monitor.analyze_content(biased_content)

            assert result.bias_scores["gender_bias"] == 0.8
            assert result.is_safe is False  # High gender bias

    @pytest.mark.asyncio
    async def test_content_filtering(self, safety_monitor):
        """Test content filtering for inappropriate topics."""
        inappropriate_content = "This story involves violence and scary themes."

        # Mock content classification
        with patch.object(safety_monitor, "_classify_content") as mock_classify:
            mock_classify.return_value = {
                "violence": 0.9,
                "scary": 0.8,
                "educational": 0.1,
            }

            result = await safety_monitor.analyze_content(inappropriate_content)

            assert result.is_safe is False
            assert "violence" in result.detected_categories
            assert result.category_scores["violence"] > 0.8

    @pytest.mark.asyncio
    async def test_age_appropriate_content_check(self, safety_monitor):
        """Test age-appropriate content checking."""
        content_for_older_kids = "This content discusses complex scientific concepts."
        target_age = 4  # Preschooler

        result = await safety_monitor.analyze_content(
            content_for_older_kids, target_age=target_age
        )

        # Should flag as potentially too advanced
        assert result.age_appropriate is False
        assert result.recommended_age > target_age

    @pytest.mark.asyncio
    async def test_real_time_monitoring(self, safety_monitor):
        """Test real-time content monitoring."""
        conversation_messages = [
            "Hello! What's your name?",
            "My name is Emma. I like ponies.",
            "That's wonderful! Tell me about your favorite pony.",
            "She's pink and has a rainbow mane!",
        ]

        # Monitor entire conversation
        conversation_analysis = await safety_monitor.analyze_conversation(
            conversation_messages
        )

        assert conversation_analysis.overall_safety == SafetyLevel.SAFE
        assert conversation_analysis.inappropriate_count == 0
        assert len(conversation_analysis.message_scores) == 4

    @pytest.mark.asyncio
    async def test_safety_threshold_adjustment(self, safety_monitor):
        """Test adjusting safety thresholds."""
        # Set stricter thresholds
        safety_monitor.set_toxicity_threshold(0.3)  # More strict
        safety_monitor.set_bias_threshold(0.2)  # More strict

        borderline_content = "Content that is borderline appropriate."

        with patch.object(safety_monitor, "_detect_toxicity", return_value=0.4):
            result = await safety_monitor.analyze_content(borderline_content)

            # Should be flagged with stricter threshold
            assert result.safety_level != SafetyLevel.SAFE

    @pytest.mark.asyncio
    async def test_safety_report_generation(self, safety_monitor):
        """Test generating safety reports."""
        session_data = {
            "session_id": "session123",
            "child_id": "child456",
            "messages": [
                "Hello teddy!",
                "Tell me a story",
                "What's 2+2?",
                "Can we play a game?",
            ],
            "duration_minutes": 15,
        }

        report = await safety_monitor.generate_safety_report(session_data)

        assert report.session_id == "session123"
        assert report.child_id == "child456"
        assert report.total_messages == 4
        assert report.safety_violations == 0
        assert report.overall_score > 0.8

    @pytest.mark.asyncio
    async def test_parental_notification_trigger(self, safety_monitor):
        """Test triggering parental notifications for safety issues."""
        concerning_content = "Content that parents should be notified about."

        with patch.object(safety_monitor, "_detect_toxicity", return_value=0.9):
            result = await safety_monitor.analyze_content(concerning_content)

            if result.safety_level == SafetyLevel.CRITICAL:
                notification_sent = await safety_monitor.notify_parents(
                    child_id="child123",
                    content=concerning_content,
                    safety_analysis=result,
                )

                assert notification_sent is True


class TestVaultClient:
    """Test Vault client functionality."""

    @pytest.fixture
    def vault_client(self):
        """Create vault client instance."""
        return VaultClient(
            vault_url="http://localhost:8200",
            vault_token="test-token",
            mount_point="secret",
        )

    @pytest.mark.asyncio
    async def test_store_secret(self, vault_client):
        """Test storing secrets in vault."""
        with patch.object(vault_client, "_make_vault_request") as mock_request:
            mock_request.return_value = {"success": True}

            result = await vault_client.store_secret("api_key", "secret_value")

            assert result is True
            mock_request.assert_called_once()

    @pytest.mark.asyncio
    async def test_retrieve_secret(self, vault_client):
        """Test retrieving secrets from vault."""
        with patch.object(vault_client, "_make_vault_request") as mock_request:
            mock_request.return_value = {
                "data": {"data": {"value": "secret_value"}}}

            result = await vault_client.retrieve_secret("api_key")

            assert result == "secret_value"
            mock_request.assert_called_once()

    @pytest.mark.asyncio
    async def test_encrypt_data(self, vault_client):
        """Test encrypting data with vault."""
        with patch.object(vault_client, "_make_vault_request") as mock_request:
            mock_request.return_value = {
                "data": {"ciphertext": "vault:v1:encrypted_data"}
            }

            result = await vault_client.encrypt("sensitive_data")

            assert result == "vault:v1:encrypted_data"
            mock_request.assert_called_once()

    @pytest.mark.asyncio
    async def test_decrypt_data(self, vault_client):
        """Test decrypting data with vault."""
        with patch.object(vault_client, "_make_vault_request") as mock_request:
            mock_request.return_value = {
                "data": {"plaintext": "c2Vuc2l0aXZlX2RhdGE="}  # base64 encoded
            }

            result = await vault_client.decrypt("vault:v1:encrypted_data")

            assert result == "sensitive_data"
            mock_request.assert_called_once()

    @pytest.mark.asyncio
    async def test_vault_health_check(self, vault_client):
        """Test vault health checking."""
        with patch.object(vault_client, "_make_vault_request") as mock_request:
            mock_request.return_value = {"sealed": False, "initialized": True}

            is_healthy = await vault_client.health_check()

            assert is_healthy is True

    @pytest.mark.asyncio
    async def test_vault_connection_error(self, vault_client):
        """Test handling vault connection errors."""
        with patch.object(vault_client, "_make_vault_request") as mock_request:
            mock_request.side_effect = ConnectionError(
                "Cannot connect to vault")

            with pytest.raises(ConnectionError):
                await vault_client.retrieve_secret("api_key")
