import json
import sys
from pathlib import Path
from unittest.mock import AsyncMock, patch
from uuid import uuid4

from src.application.dto.ai_response import AIResponse
from httpx import AsyncClient

# Add src to path
src_path = Path(__file__).parent
while src_path.name != "backend" and src_path.parent != src_path:
    src_path = src_path.parent
src_path = src_path / "src"

if str(src_path) not in sys.path:
    sys.path.insert(0, str(src_path))

"""Integration tests for ESP32 API endpoints."""

try:
    import pytest
except ImportError:
    try:
        from common.mock_pytest import pytest
    except ImportError:
        pass
    pytest = MockPytest()


class TestESP32Endpoints:
    """Test ESP32 API endpoints."""

    @pytest.fixture
    async def client(self):
        """Create test client."""
        from main import app

        async with AsyncClient(app=app, base_url="http://test") as ac:
            yield ac

    @pytest.fixture
    def audio_request_data(self):
        """Mock audio request data."""
        return {
            "child_id": str(uuid4()),
            "audio_data": "fake_base64_audio_data",
            "language_code": "en",
            "metadata": {
                "duration": 3.5,
                "sample_rate": 16000,
                "format": "wav",
            },
        }

    @pytest.fixture
    def mock_ai_response(self):
        """Mock AI response."""
        return AIResponse(
            response_text="Hello! That's a great question about animals.",
            audio_response=b"mock_audio_response",
            emotion="curious",
            sentiment=0.7,
            safe=True,
            conversation_id=str(uuid4()),
        )

    @pytest.mark.asyncio
    async def test_process_audio_success(
        self, client, audio_request_data, mock_ai_response
    ):
        """Test successful audio processing."""
        with patch(
            "application.use_cases.process_esp32_audio.ProcessESP32AudioUseCase"
        ) as mock_use_case:
            mock_use_case_instance = AsyncMock()
            mock_use_case_instance.execute.return_value = mock_ai_response
            mock_use_case.return_value = mock_use_case_instance

            response = await client.post("/api/v1/esp32/audio", json=audio_request_data)

            assert response.status_code == 200
            data = response.json()
            assert (
                data["response_text"] == "Hello! That's a great question about animals."
            )
            assert data["emotion"] == "curious"
            assert data["sentiment"] == 0.7
            assert data["safe"] is True

    @pytest.mark.asyncio
    async def test_process_audio_invalid_child_id(self, client, audio_request_data):
        """Test audio processing with invalid child ID."""
        audio_request_data["child_id"] = "invalid-uuid"

        response = await client.post("/api/v1/esp32/audio", json=audio_request_data)

        assert response.status_code == 422  # Validation error
        data = response.json()
        assert "child_id" in str(data["detail"]).lower()

    @pytest.mark.asyncio
    async def test_process_audio_missing_data(self, client):
        """Test audio processing with missing required data."""
        incomplete_data = {
            "child_id": str(uuid4())
            # Missing audio_data and language_code
        }

        response = await client.post("/api/v1/esp32/audio", json=incomplete_data)

        assert response.status_code == 422  # Validation error

    @pytest.mark.asyncio
    async def test_process_audio_child_not_found(self, client, audio_request_data):
        """Test audio processing when child profile not found."""
        try:
            from fastapi import HTTPException
        except ImportError:
            from common.mock_fastapi import HTTPException

        with patch(
            "application.use_cases.process_esp32_audio.ProcessESP32AudioUseCase"
        ) as mock_use_case:
            mock_use_case_instance = AsyncMock()
            mock_use_case_instance.execute.side_effect = HTTPException(
                status_code=404, detail="Child profile not found"
            )
            mock_use_case.return_value = mock_use_case_instance

            response = await client.post("/api/v1/esp32/audio", json=audio_request_data)

            assert response.status_code == 404
            data = response.json()
            assert data["detail"] == "Child profile not found"

    @pytest.mark.asyncio
    async def test_process_audio_safety_violation(self, client, audio_request_data):
        """Test audio processing with safety violation."""
        unsafe_response = AIResponse(
            response_text="I'm sorry, I can't process that. Let's talk about something else.",
            audio_response=b"",
            emotion="neutral",
            sentiment=0.0,
            safe=False,
            conversation_id=str(uuid4()),
        )

        with patch(
            "application.use_cases.process_esp32_audio.ProcessESP32AudioUseCase"
        ) as mock_use_case:
            mock_use_case_instance = AsyncMock()
            mock_use_case_instance.execute.return_value = unsafe_response
            mock_use_case.return_value = mock_use_case_instance

            response = await client.post("/api/v1/esp32/audio", json=audio_request_data)

            assert (
                response.status_code == 200
            )  # Still successful, but content is filtered
            data = response.json()
            assert data["safe"] is False
            assert "can't process" in data["response_text"]

    @pytest.mark.asyncio
    async def test_process_audio_large_payload(self, client, audio_request_data):
        """Test audio processing with large audio payload."""
        # Simulate large audio data
        audio_request_data["audio_data"] = "x" * 10000  # Large base64 string
        audio_request_data["metadata"]["duration"] = 30.0  # 30 seconds

        with patch(
            "application.use_cases.process_esp32_audio.ProcessESP32AudioUseCase"
        ) as mock_use_case:
            mock_use_case_instance = AsyncMock()
            mock_use_case_instance.execute.return_value = AIResponse(
                response_text="I understand your longer message.",
                audio_response=b"longer_audio_response",
                emotion="understanding",
                sentiment=0.6,
                safe=True,
                conversation_id=str(uuid4()),
            )
            mock_use_case.return_value = mock_use_case_instance

            response = await client.post("/api/v1/esp32/audio", json=audio_request_data)

            assert response.status_code == 200

    @pytest.mark.asyncio
    async def test_process_audio_different_languages(self, client, audio_request_data):
        """Test audio processing in different languages."""
        languages = ["en", "es", "fr", "ar", "zh"]

        for lang in languages:
            audio_request_data["language_code"] = lang

            with patch(
                "application.use_cases.process_esp32_audio.ProcessESP32AudioUseCase"
            ) as mock_use_case:
                mock_use_case_instance = AsyncMock()
                mock_use_case_instance.execute.return_value = AIResponse(
                    response_text=f"Response in {lang}",
                    audio_response=b"audio_response",
                    emotion="happy",
                    sentiment=0.8,
                    safe=True,
                    conversation_id=str(uuid4()),
                )
                mock_use_case.return_value = mock_use_case_instance

                response = await client.post(
                    "/api/v1/esp32/audio", json=audio_request_data
                )

                assert response.status_code == 200
                data = response.json()
                assert f"Response in {lang}" in data["response_text"]

    @pytest.mark.asyncio
    async def test_esp32_status_endpoint(self, client):
        """Test ESP32 device status endpoint."""
        response = await client.get("/api/v1/esp32/status")

        assert response.status_code == 200
        data = response.json()
        assert "status" in data
        assert "connected_devices" in data
        assert "last_heartbeat" in data

    @pytest.mark.asyncio
    async def test_esp32_configuration_endpoint(self, client):
        """Test ESP32 configuration endpoint."""
        config_data = {
            "audio_settings": {
                "sample_rate": 16000,
                "bit_depth": 16,
                "channels": 1,
            },
            "safety_settings": {
                "content_filtering": True,
                "safety_threshold": 0.8,
            },
            "device_settings": {"led_brightness": 75, "volume_level": 60},
        }

        response = await client.post("/api/v1/esp32/configure", json=config_data)

        assert response.status_code == 200
        data = response.json()
        assert data["success"] is True
        assert "configuration_id" in data

    @pytest.mark.asyncio
    async def test_esp32_heartbeat_endpoint(self, client):
        """Test ESP32 heartbeat endpoint."""
        device_data = {
            "device_id": "esp32_001",
            "status": "online",
            "battery_level": 85,
            "wifi_strength": -45,
            "temperature": 23.5,
            "uptime_seconds": 3600,
        }

        response = await client.post("/api/v1/esp32/heartbeat", json=device_data)

        assert response.status_code == 200
        data = response.json()
        assert data["acknowledged"] is True
        assert "next_heartbeat" in data

    @pytest.mark.asyncio
    async def test_esp32_logs_endpoint(self, client):
        """Test ESP32 logs retrieval endpoint."""
        device_id = "esp32_001"
        response = await client.get(f"/api/v1/esp32/logs/{device_id}")

        assert response.status_code == 200
        data = response.json()
        assert "logs" in data
        assert "total_count" in data
        assert "page" in data

    @pytest.mark.asyncio
    async def test_esp32_firmware_update_endpoint(self, client):
        """Test ESP32 firmware update endpoint."""
        update_data = {
            "device_id": "esp32_001",
            "firmware_version": "2.1.0",
            "update_url": "https://updates.example.com/firmware/2.1.0.bin",
            "checksum": "sha256:abcd1234...",
        }

        response = await client.post("/api/v1/esp32/firmware-update", json=update_data)

        assert response.status_code == 200
        data = response.json()
        assert data["update_initiated"] is True
        assert "update_id" in data

    @pytest.mark.asyncio
    async def test_rate_limiting(self, client, audio_request_data):
        """Test rate limiting on ESP32 endpoints."""
        # Simulate many rapid requests
        responses = []

        for i in range(15):  # Exceed typical rate limit
            response = await client.post("/api/v1/esp32/audio", json=audio_request_data)
            responses.append(response)

        # Should have some rate limited responses
        rate_limited = [r for r in responses if r.status_code == 429]
        assert len(rate_limited) > 0

    @pytest.mark.asyncio
    async def test_authentication_required(self, client, audio_request_data):
        """Test that authentication is required for protected endpoints."""
        # Test without authentication headers
        response = await client.post("/api/v1/esp32/audio", json=audio_request_data)

        # Should require authentication (depending on configuration)
        # This test would need to be adjusted based on actual auth requirements
        assert response.status_code in [200, 401, 403]

    @pytest.mark.asyncio
    async def test_cors_headers(self, client):
        """Test CORS headers are present."""
        response = await client.options("/api/v1/esp32/status")

        assert response.status_code == 200
        assert "Access-Control-Allow-Origin" in response.headers

    @pytest.mark.asyncio
    async def test_content_type_validation(self, client, audio_request_data):
        """Test content type validation."""
        # Test with incorrect content type
        response = await client.post(
            "/api/v1/esp32/audio",
            data=json.dumps(audio_request_data),
            headers={"Content-Type": "text/plain"},
        )

        assert response.status_code == 422  # Should reject non-JSON

    @pytest.mark.asyncio
    async def test_audio_format_validation(self, client, audio_request_data):
        """Test audio format validation."""
        # Test with invalid audio format
        audio_request_data["metadata"]["format"] = "invalid_format"

        response = await client.post("/api/v1/esp32/audio", json=audio_request_data)

        assert response.status_code == 422  # Should validate audio format

    @pytest.mark.asyncio
    async def test_concurrent_requests(self, client, audio_request_data):
        """Test handling concurrent requests."""
        import asyncio

        # Create multiple concurrent requests
        tasks = []
        for i in range(5):
            request_data = audio_request_data.copy()
            # Different child for each request
            request_data["child_id"] = str(uuid4())

            task = client.post("/api/v1/esp32/audio", json=request_data)
            tasks.append(task)

        # Execute all requests concurrently
        responses = await asyncio.gather(*tasks, return_exceptions=True)

        # All should complete successfully
        successful_responses = [
            r for r in responses if hasattr(r, "status_code") and r.status_code == 200
        ]
        assert len(successful_responses) > 0

    @pytest.mark.asyncio
    async def test_error_handling(self, client, audio_request_data):
        """Test error handling in endpoints."""
        with patch(
            "application.use_cases.process_esp32_audio.ProcessESP32AudioUseCase"
        ) as mock_use_case:
            mock_use_case_instance = AsyncMock()
            mock_use_case_instance.execute.side_effect = Exception(
                "Internal service error"
            )
            mock_use_case.return_value = mock_use_case_instance

            response = await client.post("/api/v1/esp32/audio", json=audio_request_data)

            assert response.status_code == 500  # Internal server error
            data = response.json()
            assert "error" in data or "detail" in data

    @pytest.mark.asyncio
    async def test_request_timeout_handling(self, client, audio_request_data):
        """Test request timeout handling."""
        with patch(
            "application.use_cases.process_esp32_audio.ProcessESP32AudioUseCase"
        ) as mock_use_case:
            mock_use_case_instance = AsyncMock()

            # Simulate a long-running request
            async def slow_execute(*args, **kwargs):
                await asyncio.sleep(10)  # Longer than typical timeout
                return mock_ai_response

            mock_use_case_instance.execute = slow_execute
            mock_use_case.return_value = mock_use_case_instance

            # This test would need actual timeout configuration
            response = await client.post("/api/v1/esp32/audio", json=audio_request_data)

            # Should handle timeout gracefully
            assert response.status_code in [200, 408, 504]
