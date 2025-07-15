import sys
from pathlib import Path

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
from \1st import AudioFormat


class TestPerformance:
    """Test performance characteristics"""

    @pytest.mark.asyncio
    async def test_transcription_performance_reasonable(
        self, voice_service, sample_wav_data
    ):
        """Test that transcription performance is reasonable"""
        import time

        start_time = time.time()

        result = await voice_service.transcribe_audio(
            audio_data=sample_wav_data, format=AudioFormat.WAV
        )

        end_time = time.time()
        actual_time = (end_time - start_time) * 1000  # Convert to ms

        # Processing should be reasonable (less than 10x real-time for 1s
        # audio)
        assert actual_time < 10000  # 10 seconds max for 1 second audio
        assert result.processing_time_ms > 0
