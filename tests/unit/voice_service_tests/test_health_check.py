import sys
from pathlib import Path
from unittest.mock import Mock

# Add src to path
src_path = Path(__file__).parent
while src_path.name != "backend" and src_path.parent != src_path:
    src_path = src_path.parent
src_path = src_path / "src"

if str(src_path) not in sys.path:
    sys.path.insert(0, str(src_path))


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


class TestHealthCheck:
    """Test voice service health check functionality"""

    @pytest.mark.asyncio
    async def test_health_check_returns_comprehensive_status(self, voice_service):
        """Test health check returns comprehensive system status"""
        health = await voice_service.health_check()

        assert "service" in health
        assert "providers" in health
        assert "dependencies" in health
        assert "config" in health

        assert health["service"] == "healthy"
        assert "whisper" in health["dependencies"]
        assert "azure_speech" in health["dependencies"]
        assert "pydub" in health["dependencies"]

        assert "default_provider" in health["config"]
        assert "supported_formats" in health["config"]

    @pytest.mark.asyncio
    async def test_health_check_with_whisper_available(self, voice_service):
        """Test health check when Whisper is available"""
        # Mock Whisper model
        mock_model = Mock()
        mock_model.transcribe.return_value = {"text": "test"}
        voice_service.whisper_model = mock_model

        health = await voice_service.health_check()

        assert health["providers"]["whisper"] == "healthy"

    @pytest.mark.asyncio
    async def test_health_check_with_azure_configured(self, voice_service):
        """Test health check when Azure is configured"""
        # Mock Azure config
        voice_service.azure_speech_config = Mock()

        health = await voice_service.health_check()

        assert health["providers"]["azure"] == "configured"
