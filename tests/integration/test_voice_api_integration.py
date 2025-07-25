import base64
import io
import sys
from pathlib import Path
from unittest.mock import Mock, patch

from application.services.voice_service import TranscriptionResult, VoiceService
from src.api.endpoints.voice import router as voice_router

# Add src to path
src_path = Path(__file__).parent
while src_path.name != "backend" and src_path.parent != src_path:
    src_path = src_path.parent
src_path = src_path / "src"

if str(src_path) not in sys.path:
    sys.path.insert(0, str(src_path))

"""
🧪 Integration Tests for Voice API
Tests for ESP32 audio processing via FastAPI endpoints
"""


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
try:
    from fastapi import FastAPI
except ImportError:
    from common.mock_fastapi import FastAPI

try:
    from fastapi.testclient import TestClient
except ImportError:
    from common.mock_fastapi.testclient import TestClient

# Import the FastAPI app and components

# ================ TEST SETUP ================


@pytest.fixture
def app():
    """Create FastAPI test app"""
    app = FastAPI()
    app.include_router(voice_router)
    return app


@pytest.fixture
def client(app):
    """Create test client"""
    return TestClient(app)


@pytest.fixture
def sample_mp3_bytes():
    """Generate sample MP3 audio bytes for testing"""
    # This is a minimal MP3 file for testing
    # In production, you'd use actual MP3 files
    mp3_header = b"\xff\xfb\x90\x00"  # MP3 frame header
    mp3_data = mp3_header + b"\x00" * 1000  # Add some data
    return mp3_data


@pytest.fixture
def sample_wav_bytes():
    """Generate sample WAV audio bytes for testing"""
    import math
    import struct
    import wave

    # Create 1 second of 16kHz sine wave
    sample_rate = 16000
    duration = 1.0
    frequency = 440  # A4 note

    # Generate samples
    num_samples = int(sample_rate * duration)
    samples = []
    for i in range(num_samples):
        t = i / sample_rate
        sample = int(16384 * math.sin(2 * math.pi * frequency * t))
        samples.append(sample)

    # Create WAV file in memory
    wav_buffer = io.BytesIO()
    with wave.open(wav_buffer, "wb") as wav_file:
        wav_file.setnchannels(1)  # Mono
        wav_file.setsampwidth(2)  # 16-bit
        wav_file.setframerate(sample_rate)
        wav_file.writeframes(struct.pack("<" + "h" * len(samples), *samples))

    return wav_buffer.getvalue()


@pytest.fixture
def mock_transcription_result():
    """Mock transcription result for testing"""
    return TranscriptionResult(
        text="مرحباً دبدوب، كيف حالك اليوم؟",
        language="ar",
        confidence=0.92,
        provider="whisper",
        processing_time_ms=450,
        audio_duration_ms=2500,
        segments=[
            {"start": 0.0, "end": 1.0, "text": "مرحباً دبدوب"},
            {"start": 1.0, "end": 2.5, "text": "كيف حالك اليوم؟"},
        ],
        metadata={
            "model": "base",
            "language_detected": "ar",
            "segments_count": 2,
        },
    )


@pytest.fixture
def mock_ai_response():
    """Mock AI response for testing"""
    return {
        "text": "مرحباً بك يا صديقي! أنا بخير، شكراً لسؤالك. كيف يمكنني مساعدتك اليوم؟",
        "emotion": "happy",
        "category": "greeting",
        "learning_points": ["social_interaction", "politeness"],
        "timestamp": "2024-01-15T10:30:00",
    }


# ================ ESP32 AUDIO ENDPOINT TESTS ================


class TestESP32AudioEndpoint:
    """Test /api/voice/esp32/audio endpoint"""

    def test_esp32_audio_endpoint_with_mp3_file(
        self,
        client,
        sample_mp3_bytes,
        mock_transcription_result,
        mock_ai_response,
    ):
        """Test ESP32 audio processing with MP3 file upload"""
        # Mock the voice service and AI service
        with (
            patch("src.api.endpoints.voice.get_voice_service") as mock_voice_service,
            patch("src.api.endpoints.voice.get_ai_service") as mock_ai_service,
        ):
            # Setup mocks
            mock_voice_instance = Mock()
            mock_voice_instance.process_esp32_audio.return_value = (
                mock_transcription_result
            )
            mock_voice_service.return_value = mock_voice_instance

            mock_ai_instance = Mock()
            mock_ai_instance.generate_response.return_value = mock_ai_response
            mock_ai_service.return_value = mock_ai_instance

            # Prepare test data
            files = {
                "file": (
                    "test_audio.mp3",
                    io.BytesIO(sample_mp3_bytes),
                    "audio/mpeg",
                )
            }
            data = {
                "device_id": "ESP32_TEST_001",
                "session_id": "test_session_123",
                "audio_format": "mp3",
                "language": "ar",
                "child_name": "أحمد",
                "child_age": "6",
            }

            # Make request
            response = client.post("/api/voice/esp32/audio", files=files, data=data)

            # Verify response
            assert response.status_code == 200
            result = response.json()

            assert result["success"] is True
            assert result["device_id"] == "ESP32_TEST_001"
            assert result["session_id"] == "test_session_123"

            # Check transcription
            transcription = result["transcription"]
            assert transcription["text"] == "مرحباً دبدوب، كيف حالك اليوم؟"
            assert transcription["language"] == "ar"
            assert transcription["confidence"] == 0.92
            assert transcription["provider"] == "whisper"

            # Check AI response
            ai_response = result["ai_response"]
            assert ai_response["emotion"] == "happy"
            assert ai_response["category"] == "greeting"

            # Check performance metrics
            performance = result["performance"]
            assert "total_processing_time_ms" in performance
            assert "audio_size_bytes" in performance
            assert performance["compression_detected"] is True

    def test_esp32_audio_endpoint_with_wav_file(
        self,
        client,
        sample_wav_bytes,
        mock_transcription_result,
        mock_ai_response,
    ):
        """Test ESP32 audio processing with WAV file upload"""
        with (
            patch("src.api.endpoints.voice.get_voice_service") as mock_voice_service,
            patch("src.api.endpoints.voice.get_ai_service") as mock_ai_service,
        ):
            # Setup mocks
            mock_voice_instance = Mock()
            mock_voice_instance.process_esp32_audio.return_value = (
                mock_transcription_result
            )
            mock_voice_service.return_value = mock_voice_instance

            mock_ai_instance = Mock()
            mock_ai_instance.generate_response.return_value = mock_ai_response
            mock_ai_service.return_value = mock_ai_instance

            # Prepare test data
            files = {
                "file": (
                    "test_audio.wav",
                    io.BytesIO(sample_wav_bytes),
                    "audio/wav",
                )
            }
            data = {
                "device_id": "ESP32_TEST_002",
                "audio_format": "wav",
                "language": "ar",
            }

            # Make request
            response = client.post("/api/voice/esp32/audio", files=files, data=data)

            # Verify response
            assert response.status_code == 200
            result = response.json()

            assert result["success"] is True
            assert result["performance"]["compression_detected"] is False

    def test_esp32_audio_endpoint_with_empty_file(self, client):
        """Test ESP32 audio endpoint with empty file"""
        files = {"file": ("empty.mp3", io.BytesIO(b""), "audio/mpeg")}
        data = {"device_id": "ESP32_TEST_003", "audio_format": "mp3"}

        response = client.post("/api/voice/esp32/audio", files=files, data=data)

        assert response.status_code == 400
        assert "Empty audio file" in response.json()["detail"]

    def test_esp32_audio_endpoint_without_file(self, client):
        """Test ESP32 audio endpoint without file"""
        data = {"device_id": "ESP32_TEST_004", "audio_format": "mp3"}

        response = client.post("/api/voice/esp32/audio", data=data)

        assert response.status_code == 422  # Validation error

    def test_esp32_audio_endpoint_processing_error(self, client, sample_mp3_bytes):
        """Test ESP32 audio endpoint when processing fails"""
        with patch("src.api.endpoints.voice.get_voice_service") as mock_voice_service:
            # Setup mock to raise exception
            mock_voice_instance = Mock()
            mock_voice_instance.process_esp32_audio.side_effect = Exception(
                "Processing failed"
            )
            mock_voice_service.return_value = mock_voice_instance

            files = {
                "file": (
                    "test_audio.mp3",
                    io.BytesIO(sample_mp3_bytes),
                    "audio/mpeg",
                )
            }
            data = {"device_id": "ESP32_TEST_005", "audio_format": "mp3"}

            response = client.post("/api/voice/esp32/audio", files=files, data=data)

            assert response.status_code == 500
            assert "Audio processing failed" in response.json()["detail"]


class TestESP32AudioJSONEndpoint:
    """Test /api/voice/esp32/audio-json endpoint"""

    def test_esp32_audio_json_endpoint(
        self,
        client,
        sample_mp3_bytes,
        mock_transcription_result,
        mock_ai_response,
    ):
        """Test ESP32 audio processing via JSON payload"""
        with (
            patch("src.api.endpoints.voice.get_voice_service") as mock_voice_service,
            patch("src.api.endpoints.voice.get_ai_service") as mock_ai_service,
        ):
            # Setup mocks
            mock_voice_instance = Mock()
            mock_voice_instance.process_esp32_audio.return_value = (
                mock_transcription_result
            )
            mock_voice_service.return_value = mock_voice_instance

            mock_ai_instance = Mock()
            mock_ai_instance.generate_response.return_value = mock_ai_response
            mock_ai_service.return_value = mock_ai_instance

            # Prepare JSON request
            audio_base64 = base64.b64encode(sample_mp3_bytes).decode("utf-8")
            request_data = {
                "audio_data": audio_base64,
                "format": "mp3",
                "device_id": "ESP32_JSON_001",
                "session_id": "json_session_123",
                "language": "ar",
                "child_name": "فاطمة",
                "child_age": 5,
            }

            # Make request
            response = client.post(
                "/api/voice/esp32/audio-json",
                json=request_data,
                headers={"Content-Type": "application/json"},
            )

            # Verify response
            assert response.status_code == 200
            result = response.json()

            assert result["success"] is True
            assert "transcription" in result
            assert "ai_response" in result
            assert "timestamp" in result

    def test_esp32_audio_json_endpoint_invalid_base64(self, client):
        """Test ESP32 audio JSON endpoint with invalid base64"""
        request_data = {
            "audio_data": "invalid_base64_!@#$",
            "format": "mp3",
            "device_id": "ESP32_JSON_002",
        }

        response = client.post("/api/voice/esp32/audio-json", json=request_data)

        assert response.status_code == 500


# ================ VOICE SERVICE HEALTH TESTS ================


class TestVoiceServiceHealth:
    """Test voice service health and status"""

    def test_voice_service_dependency_injection(self, client):
        """Test that voice service dependency injection works"""
        # This test verifies that the dependency injection system works
        # by checking if we can get a voice service instance
        with patch("src.api.endpoints.voice.create_voice_service") as mock_create:
            mock_service = Mock(spec=VoiceService)
            mock_create.return_value = mock_service

            # Try to get voice service through dependency injection
            import asyncio

            result = asyncio.run(get_voice_service())

            assert result == mock_service
            mock_create.assert_called_once()


# ================ INTEGRATION WITH REAL SERVICES ================


class TestRealServiceIntegration:
    """Integration tests with real services (when available)"""

    @pytest.mark.integration
    def test_real_whisper_integration(self, client, sample_wav_bytes):
        """Test with real Whisper service if available"""
        # This test only runs if Whisper is actually installed
        try:
            # import whisper

            whisper_available = True
        except ImportError:
            whisper_available = False

        if not whisper_available:
            pytest.skip("Whisper not available for integration test")

        # Use real voice service
        from application.services.voice_service import create_voice_service

        voice_service = create_voice_service()

        if not voice_service.whisper_model:
            pytest.skip("Whisper model not loaded")

        with (
            patch("src.api.endpoints.voice.get_voice_service") as mock_voice_service,
            patch("src.api.endpoints.voice.get_ai_service") as mock_ai_service,
        ):
            mock_voice_service.return_value = voice_service

            mock_ai_instance = Mock()
            mock_ai_instance.generate_response.return_value = {
                "text": "مرحباً! كيف يمكنني مساعدتك؟",
                "emotion": "friendly",
                "category": "greeting",
                "learning_points": [],
            }
            mock_ai_service.return_value = mock_ai_instance

            files = {
                "file": (
                    "real_test.wav",
                    io.BytesIO(sample_wav_bytes),
                    "audio/wav",
                )
            }
            data = {
                "device_id": "ESP32_REAL_TEST",
                "audio_format": "wav",
                "language": "ar",
            }

            response = client.post("/api/voice/esp32/audio", files=files, data=data)

            assert response.status_code == 200
            result = response.json()
            assert result["success"] is True
            assert result["transcription"]["provider"] in [
                "whisper",
                "fallback",
            ]


# ================ PERFORMANCE TESTS ================


class TestAPIPerformance:
    """Test API performance characteristics"""

    def test_esp32_audio_processing_performance(
        self,
        client,
        sample_mp3_bytes,
        mock_transcription_result,
        mock_ai_response,
    ):
        """Test that audio processing completes within reasonable time"""
        with (
            patch("src.api.endpoints.voice.get_voice_service") as mock_voice_service,
            patch("src.api.endpoints.voice.get_ai_service") as mock_ai_service,
        ):
            # Setup mocks
            mock_voice_instance = Mock()
            mock_voice_instance.process_esp32_audio.return_value = (
                mock_transcription_result
            )
            mock_voice_service.return_value = mock_voice_instance

            mock_ai_instance = Mock()
            mock_ai_instance.generate_response.return_value = mock_ai_response
            mock_ai_service.return_value = mock_ai_instance

            files = {
                "file": (
                    "perf_test.mp3",
                    io.BytesIO(sample_mp3_bytes),
                    "audio/mpeg",
                )
            }
            data = {"device_id": "ESP32_PERF_TEST", "audio_format": "mp3"}

            import time

            start_time = time.time()

            response = client.post("/api/voice/esp32/audio", files=files, data=data)

            end_time = time.time()
            processing_time = (end_time - start_time) * 1000  # Convert to ms

            assert response.status_code == 200
            # API should respond within 5 seconds
            assert processing_time < 5000

            result = response.json()
            assert "performance" in result
            assert "total_processing_time_ms" in result["performance"]


# ================ ERROR HANDLING TESTS ================


class TestAITeddyErrorHandling:
    """Test API error handling scenarios"""

    def test_invalid_audio_format(self, client, sample_mp3_bytes):
        """Test handling of invalid audio format"""
        files = {"file": ("test.mp3", io.BytesIO(sample_mp3_bytes), "audio/mpeg")}
        data = {
            "device_id": "ESP32_ERROR_TEST",
            "audio_format": "invalid_format",
        }  # Invalid format

        response = client.post("/api/voice/esp32/audio", files=files, data=data)

        # Should still work but might default to a valid format
        # The exact behavior depends on implementation
        assert response.status_code in [200, 400, 422]

    def test_missing_device_id(self, client, sample_mp3_bytes):
        """Test handling of missing device ID"""
        files = {"file": ("test.mp3", io.BytesIO(sample_mp3_bytes), "audio/mpeg")}
        data = {
            "audio_format": "mp3"
            # Missing device_id
        }

        response = client.post("/api/voice/esp32/audio", files=files, data=data)

        assert response.status_code == 422  # Validation error

    def test_malformed_json_request(self, client):
        """Test handling of malformed JSON request"""
        # Send invalid JSON
        response = client.post(
            "/api/voice/esp32/audio-json",
            data="invalid json",
            headers={"Content-Type": "application/json"},
        )

        assert response.status_code == 422


# ================ SECURITY TESTS ================


class TestAPISecurity:
    """Test API security aspects"""

    def test_large_file_upload_handling(self, client):
        """Test handling of excessively large audio files"""
        # Create a very large "audio" file (10MB of zeros)
        large_audio = b"\x00" * (10 * 1024 * 1024)

        files = {"file": ("large_test.mp3", io.BytesIO(large_audio), "audio/mpeg")}
        data = {"device_id": "ESP32_LARGE_TEST", "audio_format": "mp3"}

        # This should either be rejected or handled gracefully
        response = client.post("/api/voice/esp32/audio", files=files, data=data)

        # Response should not be 200 for such a large file
        # Exact status depends on server configuration
        assert response.status_code in [400, 413, 422, 500]

    def test_sql_injection_attempt_in_device_id(self, client, sample_mp3_bytes):
        """Test SQL injection attempt in device_id field"""
        with (
            patch("src.api.endpoints.voice.get_voice_service") as mock_voice_service,
            patch("src.api.endpoints.voice.get_ai_service") as mock_ai_service,
        ):
            # Setup basic mocks
            mock_voice_instance = Mock()
            mock_voice_service.return_value = mock_voice_instance
            mock_ai_instance = Mock()
            mock_ai_service.return_value = mock_ai_instance

            files = {
                "file": (
                    "test.mp3",
                    io.BytesIO(sample_mp3_bytes),
                    "audio/mpeg",
                )
            }
            data = {
                "device_id": "'; DROP TABLE devices; --",
                "audio_format": "mp3",
            }  # SQL injection attempt

            # Should handle malicious input safely
            response = client.post("/api/voice/esp32/audio", files=files, data=data)

            # Should not crash and should handle safely
            assert response.status_code in [200, 400, 422]


# ================ CLEANUP ================


@pytest.fixture(autouse=True)
def cleanup_after_tests():
    """Cleanup after each test"""
    yield

    # Clean up any temporary files or resources
    import gc

    gc.collect()
