"""Unit tests for COPPA consent verification system
Ensures parental consent is properly enforced across all child data collection points
"""

from unittest.mock import AsyncMock, MagicMock, patch

import pytest
from fastapi import HTTPException

from src.infrastructure.security.child_safety.consent_manager import COPPAConsentManager
from src.presentation.api.middleware.consent_verification import (
    ConsentVerificationMiddleware,
    ConsentVerificationRoute,
    require_consent,
)


class TestConsentVerificationRoute:
    """Test consent verification at route level"""

    @pytest.fixture
    def mock_consent_manager(self):
        """Mock consent manager for testing"""
        manager = AsyncMock(spec=COPPAConsentManager)
        return manager

    @pytest.fixture
    def mock_request(self):
        """Mock FastAPI request for testing"""
        request = MagicMock()
        request.path_params = {"child_id": "child_123"}
        request.query_params = {}
        request.method = "POST"
        request.url.path = "/api/v1/process-audio"
        request.headers = {"user-agent": "test-client"}
        request.client.host = "127.0.0.1"
        request.state.user = {
            "user_id": "parent_123",
            "email": "parent@test.com",
        }
        return request

    @pytest.mark.asyncio
    async def test_extract_child_id_from_path_params(self):
        """Test extracting child_id from path parameters"""
        route = ConsentVerificationRoute(
            path="/children/{child_id}",
            endpoint=lambda: None,
            require_consent_types=["data_collection"],
        )

        request = MagicMock()
        request.path_params = {"child_id": "child_123"}
        request.query_params = {}
        request.method = "GET"

        child_id = await route._extract_child_id(request)
        assert child_id == "child_123"

    @pytest.mark.asyncio
    async def test_extract_child_id_from_request_body(self):
        """Test extracting child_id from JSON request body"""
        route = ConsentVerificationRoute(
            path="/process-audio",
            endpoint=lambda: None,
            require_consent_types=["voice_recording"],
        )

        request = MagicMock()
        request.path_params = {}
        request.query_params = {}
        request.method = "POST"
        request.body = AsyncMock(
            return_value=b'{"child_id": "child_456", "audio_data": "base64data"}'
        )

        child_id = await route._extract_child_id(request)
        assert child_id == "child_456"

    @pytest.mark.asyncio
    async def test_verify_consent_success(self, mock_consent_manager):
        """Test successful consent verification"""
        # Mock consent manager to return True for all consent types
        mock_consent_manager.verify_parental_consent = AsyncMock(return_value=True)

        route = ConsentVerificationRoute(
            path="/children/{child_id}",
            endpoint=lambda: None,
            require_consent_types=["data_collection", "voice_recording"],
        )

        request = MagicMock()
        request.state.user = {"user_id": "parent_123"}

        with patch(
            "src.presentation.api.middleware.consent_verification.get_consent_manager",
            return_value=mock_consent_manager,
        ):
            # Should not raise any exception
            await route._verify_consent(request, "child_123")

            # Verify consent manager was called for each consent type
            assert mock_consent_manager.verify_parental_consent.call_count == 2

    @pytest.mark.asyncio
    async def test_verify_consent_failure(self, mock_consent_manager):
        """Test consent verification failure"""

        # Mock consent manager to return False for voice_recording
        async def mock_verify(parent_id, child_id, consent_type):
            if consent_type == "voice_recording":
                return False
            return True

        mock_consent_manager.verify_parental_consent = AsyncMock(
            side_effect=mock_verify
        )

        route = ConsentVerificationRoute(
            path="/process-audio",
            endpoint=lambda: None,
            require_consent_types=["data_collection", "voice_recording"],
        )

        request = MagicMock()
        request.state.user = {"user_id": "parent_123"}

        with patch(
            "src.presentation.api.middleware.consent_verification.get_consent_manager",
            return_value=mock_consent_manager,
        ):
            # Should raise HTTPException for missing consent
            with pytest.raises(HTTPException) as exc_info:
                await route._verify_consent(request, "child_123")

            assert exc_info.value.status_code == 403
            assert "voice_recording" in str(exc_info.value.detail)

    @pytest.mark.asyncio
    async def test_verify_consent_no_user(self):
        """Test consent verification when no user is authenticated"""
        route = ConsentVerificationRoute(
            path="/children/{child_id}",
            endpoint=lambda: None,
            require_consent_types=["data_collection"],
        )

        request = MagicMock()
        request.state.user = None

        # Should raise HTTPException for missing authentication
        with pytest.raises(HTTPException) as exc_info:
            await route._verify_consent(request, "child_123")

        assert exc_info.value.status_code == 401
        assert "authentication required" in str(exc_info.value.detail).lower()

    @pytest.mark.asyncio
    async def test_log_data_collection(self):
        """Test data collection audit logging"""
        route = ConsentVerificationRoute(
            path="/children/{child_id}",
            endpoint=lambda: None,
            require_consent_types=["data_collection"],
        )

        request = MagicMock()
        request.method = "POST"
        request.url.path = "/api/v1/children/child_123"
        request.headers = {"user-agent": "test-client"}
        request.client.host = "127.0.0.1"

        # Should not raise any exception
        await route._log_data_collection(request, "child_123")


class TestConsentVerificationMiddleware:
    """Test consent verification middleware"""

    @pytest.mark.asyncio
    async def test_middleware_path_matching(self):
        """Test middleware correctly identifies paths requiring consent"""
        app = MagicMock()

        consent_paths = {
            "/api/v1/process-audio": ["data_collection", "voice_recording"],
            "/api/v1/children": ["data_collection"],
        }

        middleware = ConsentVerificationMiddleware(app, consent_paths)

        # Test matching path
        scope = {
            "type": "http",
            "path": "/api/v1/process-audio",
            "method": "POST",
        }

        receive = AsyncMock()
        send = AsyncMock()

        # Mock request with child_id
        with patch(
            "src.presentation.api.middleware.consent_verification.Request"
        ) as mock_request_class:
            mock_request = MagicMock()
            mock_request.url.path = "/api/v1/process-audio"
            mock_request_class.return_value = mock_request

            # Mock route extraction
            with patch.object(
                ConsentVerificationRoute,
                "_extract_child_id",
                return_value="child_123",
            ) as mock_extract:
                with patch.object(
                    ConsentVerificationRoute, "_verify_consent"
                ) as mock_verify:
                    await middleware(scope, receive, send)

                    # Verify consent verification was called
                    mock_verify.assert_called_once()


class TestRequireConsentDecorator:
    """Test @require_consent decorator"""

    def test_decorator_adds_consent_types(self):
        """Test that decorator adds consent types to function"""

        @require_consent("data_collection", "voice_recording")
        def test_function():
            pass

        assert hasattr(test_function, "_consent_types")
        assert test_function._consent_types == [
            "data_collection",
            "voice_recording",
        ]

    def test_decorator_with_single_consent(self):
        """Test decorator with single consent type"""

        @require_consent("usage_analytics")
        def test_function():
            pass

        assert test_function._consent_types == ["usage_analytics"]


class TestConsentIntegration:
    """Integration tests for consent verification system"""

    @pytest.mark.asyncio
    async def test_full_consent_workflow(self):
        """Test complete consent verification workflow"""
        # Test the full workflow from request to verification

        # 1. Mock consent manager
        consent_manager = AsyncMock(spec=COPPAConsentManager)
        consent_manager.verify_parental_consent = AsyncMock(return_value=True)

        # 2. Create route with consent requirements
        route = ConsentVerificationRoute(
            path="/process-audio",
            endpoint=lambda: {"status": "success"},
            require_consent_types=["data_collection", "voice_recording"],
        )

        # 3. Mock request with all required data
        request = MagicMock()
        request.path_params = {"child_id": "child_123"}
        request.query_params = {}
        request.method = "POST"
        request.url.path = "/api/v1/process-audio"
        request.headers = {"user-agent": "test-client"}
        request.client.host = "127.0.0.1"
        request.state.user = {
            "user_id": "parent_123",
            "email": "parent@test.com",
        }

        # 4. Test the workflow
        with patch(
            "src.presentation.api.middleware.consent_verification.get_consent_manager",
            return_value=consent_manager,
        ):

            # Extract child_id
            child_id = await route._extract_child_id(request)
            assert child_id == "child_123"

            # Verify consent
            await route._verify_consent(request, child_id)

            # Log data collection
            await route._log_data_collection(request, child_id)

            # Verify all consent types were checked
            assert consent_manager.verify_parental_consent.call_count == 2

    @pytest.mark.asyncio
    async def test_consent_enforcement_edge_cases(self):
        """Test edge cases in consent enforcement"""
        # Test with missing child_id
        route = ConsentVerificationRoute(
            path="/test",
            endpoint=lambda: None,
            require_consent_types=["data_collection"],
        )

        request = MagicMock()
        request.path_params = {}
        request.query_params = {}
        request.method = "GET"

        child_id = await route._extract_child_id(request)
        assert child_id is None

        # Test with malformed JSON in body
        request.method = "POST"
        request.body = AsyncMock(return_value=b"invalid json")

        child_id = await route._extract_child_id(request)
        assert child_id is None
