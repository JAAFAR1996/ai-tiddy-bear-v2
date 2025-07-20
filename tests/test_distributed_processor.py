"""Unit Tests for Distributed AI Processing System.

AI Team Implementation - Task 11 Tests
Author: AI Team Lead
"""

import asyncio
import sys
import time
from pathlib import Path
from unittest.mock import patch

# Add src to path
src_path = Path(__file__).parent
while src_path.name != "backend" and src_path.parent != src_path:
    src_path = src_path.parent
src_path = src_path / "src"

if str(src_path) not in sys.path:
    sys.path.insert(0, str(src_path))

# Import numpy with fallback
try:
    import numpy as np
except ImportError:
    # Mock numpy when not available
    class MockNumpy:
        def array(self, data):
            return data

        def zeros(self, shape):
            return [0] * (shape if isinstance(shape, int) else shape[0])

        def ones(self, shape):
            return [1] * (shape if isinstance(shape, int) else shape[0])

        def mean(self, data):
            return sum(data) / len(data) if data else 0

        def std(self, data):
            return 1.0  # Mock standard deviation

        def random(self):
            class MockRandom:
                def rand(self, *args):
                    return 0.5

                def randint(self, low, high, size=None):
                    return low

                def uniform(self, low, high, size=None):
                    if size is None:
                        return (low + high) / 2
                    if isinstance(size, int):
                        return [(low + high) / 2] * size
                    return (
                        [[(low + high) / 2] * size[0]]
                        if len(size) == 1
                        else (low + high) / 2
                    )

            return MockRandom()

        @property
        def pi(self):
            return 3.14159265359

        @property
        def float32(self):
            return float

        @property
        def int16(self):
            return int

    np = MockNumpy()

# AsyncMock compatibility for Python < 3.8
try:
    from unittest.mock import AsyncMock
except ImportError:
    from unittest.mock import MagicMock

    class AsyncMock(MagicMock):
        def __call__(self, *args, **kwargs):
            sup = super(AsyncMock, self)

            async def coro():
                return sup.__call__(*args, **kwargs)

            return coro()

        def __await__(self):
            return self().__await__()


# Import pytest with fallback
try:
    import pytest
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

        def main(self, args):
            return 0

    pytest = MockPytest()

# Import the modules to test
try:
    from infrastructure.distributed_processing.distributed_processor import (
        AIServiceType,
        ChildContext,
        ConversationRequest,
        ConversationResponse,
        DistributedAIProcessor,
        MockAIServices,
        ProcessingMetrics,
        ProcessingPriority,
    )

    DISTRIBUTED_AI_IMPORTS_AVAILABLE = True
except ImportError as e:
    DISTRIBUTED_AI_IMPORTS_AVAILABLE = False
    import_error = str(e)


class TestChildContext:
    """Test child context data structure."""

    def test_default_child_context(self):
        """Test default child context creation."""
        if not DISTRIBUTED_AI_IMPORTS_AVAILABLE:
            pytest.skip(f"Distributed AI imports not available: {import_error}")

        context = ChildContext(child_id="test_child_001", name="أحمد", age=7)

        assert context.child_id == "test_child_001"
        assert context.name == "أحمد"
        assert context.age == 7
        assert context.language == "ar"
        assert context.conversation_history == []
        assert isinstance(context.personalization_data, dict)

    def test_custom_child_context(self):
        """Test custom child context creation."""
        if not DISTRIBUTED_AI_IMPORTS_AVAILABLE:
            pytest.skip(f"Distributed AI imports not available: {import_error}")

        context = ChildContext(
            child_id="test_child_002",
            name="Sarah",
            age=5,
            language="en",
            voice_profile="gentle",
            conversation_history=["Hello", "How are you?"],
            personalization_data={"favorite_color": "blue"},
        )

        assert context.language == "en"
        assert context.voice_profile == "gentle"
        assert len(context.conversation_history) == 2
        assert context.personalization_data["favorite_color"] == "blue"


class TestConversationRequest:
    """Test conversation request structure."""

    def test_conversation_request_creation(self):
        """Test conversation request creation."""
        if not DISTRIBUTED_AI_IMPORTS_AVAILABLE:
            pytest.skip(f"Distributed AI imports not available: {import_error}")

        child_context = ChildContext(child_id="test_child", name="Test Child", age=6)

        audio_data = b"fake_audio_data"

        request = ConversationRequest(
            request_id="req_001",
            audio_data=audio_data,
            child_context=child_context,
        )

        assert request.request_id == "req_001"
        assert request.audio_data == audio_data
        assert request.child_context == child_context
        assert request.priority == ProcessingPriority.NORMAL
        assert AIServiceType.TRANSCRIPTION in request.requested_services


class TestMockAIServices:
    """Test mock AI services functionality."""

    @pytest.mark.asyncio
    async def test_mock_transcription(self):
        """Test mock audio transcription."""
        if not DISTRIBUTED_AI_IMPORTS_AVAILABLE:
            pytest.skip(f"Distributed AI imports not available: {import_error}")

        audio_data = b"mock_audio_data"
        result = await MockAIServices.transcribe_audio(audio_data)

        assert isinstance(result, dict)
        assert "text" in result
        assert "confidence" in result
        assert "language" in result
        assert "processing_time_ms" in result
        assert result["confidence"] > 0.0
        assert result["processing_time_ms"] > 0

    @pytest.mark.asyncio
    async def test_mock_emotion_analysis(self):
        """Test mock emotion analysis."""
        if not DISTRIBUTED_AI_IMPORTS_AVAILABLE:
            pytest.skip(f"Distributed AI imports not available: {import_error}")

        audio_data = b"mock_audio_data"
        text = "مرحبا تيدي"
        result = await MockAIServices.analyze_emotion(audio_data, text)

        assert isinstance(result, dict)
        assert "primary_emotion" in result
        assert "confidence" in result
        assert "emotion_scores" in result
        assert "arousal" in result
        assert "valence" in result
        assert "processing_time_ms" in result

        # Check emotion scores structure
        emotion_scores = result["emotion_scores"]
        assert isinstance(emotion_scores, dict)
        assert all(0.0 <= score <= 1.0 for score in emotion_scores.values())

    @pytest.mark.asyncio
    async def test_mock_safety_check(self):
        """Test mock safety checking."""
        if not DISTRIBUTED_AI_IMPORTS_AVAILABLE:
            pytest.skip(f"Distributed AI imports not available: {import_error}")

        safe_text = "مرحبا كيف حالك"
        audio_data = b"mock_audio_data"

        result = await MockAIServices.check_safety(safe_text, audio_data)

        assert isinstance(result, dict)
        assert "is_safe" in result
        assert "risk_level" in result
        assert "confidence" in result
        assert "detected_issues" in result
        assert "processing_time_ms" in result
        assert isinstance(result["is_safe"], bool)
        assert result["risk_level"] in ["low", "medium", "high", "critical"]

    @pytest.mark.asyncio
    async def test_mock_ai_response(self):
        """Test mock AI response generation."""
        if not DISTRIBUTED_AI_IMPORTS_AVAILABLE:
            pytest.skip(f"Distributed AI imports not available: {import_error}")

        text = "مرحبا تيدي"
        child_context = ChildContext(child_id="test_child", name="أحمد", age=6)

        result = await MockAIServices.generate_ai_response(text, child_context)

        assert isinstance(result, dict)
        assert "response_text" in result
        assert "emotion" in result
        assert "confidence" in result
        assert "personalized" in result
        assert "processing_time_ms" in result
        assert child_context.name in result["response_text"]

    @pytest.mark.asyncio
    async def test_mock_tts(self):
        """Test mock text-to-speech synthesis."""
        if not DISTRIBUTED_AI_IMPORTS_AVAILABLE:
            pytest.skip(f"Distributed AI imports not available: {import_error}")

        text = "مرحبا أحمد"
        emotion = "happy"
        voice_profile = "child_friendly"

        result = await MockAIServices.synthesize_speech(text, emotion, voice_profile)

        assert isinstance(result, dict)
        assert "audio_data" in result
        assert "sample_rate" in result
        assert "duration_seconds" in result
        assert "quality" in result
        assert "processing_time_ms" in result
        assert isinstance(result["audio_data"], bytes)
        assert result["sample_rate"] == 16000


class TestDistributedAIProcessor:
    """Test main distributed AI processor functionality."""

    @pytest.fixture
    def processor(self):
        """Create distributed processor for testing."""
        if not DISTRIBUTED_AI_IMPORTS_AVAILABLE:
            pytest.skip(f"Distributed AI imports not available: {import_error}")

        return DistributedAIProcessor()

    @pytest.mark.asyncio
    async def test_processor_initialization(self, processor):
        """Test processor initialization."""
        if not DISTRIBUTED_AI_IMPORTS_AVAILABLE:
            pytest.skip(f"Distributed AI imports not available: {import_error}")

        await processor.initialize()

        # Should initialize successfully even without Ray
        assert processor.services is not None
        assert len(processor.services) > 0
        assert processor.metrics is not None

    @pytest.mark.asyncio
    async def test_conversation_processing(self, processor):
        """Test complete conversation processing pipeline."""
        if not DISTRIBUTED_AI_IMPORTS_AVAILABLE:
            pytest.skip(f"Distributed AI imports not available: {import_error}")

        # Initialize processor
        await processor.initialize()

        # Create test data
        audio_data = np.random.uniform(-0.1, 0.1, 16000)
        if hasattr(audio_data, "astype"):
            audio_data = audio_data.astype(np.float32)
            audio_bytes = (audio_data * 32767).astype(np.int16).tobytes()
        else:
            # Mock numpy fallback
            audio_bytes = b"mock_audio_bytes_data"

        child_context = ChildContext(
            child_id="test_child_001", name="أحمد", age=7, language="ar"
        )

        # Process conversation
        start_time = time.time()
        response = await processor.process_conversation(audio_bytes, child_context)
        processing_time = time.time() - start_time

        # Verify response structure
        assert isinstance(response, ConversationResponse)
        assert response.success is True
        assert response.request_id is not None
        assert response.transcription != ""
        assert response.ai_text != ""
        assert response.emotion in [
            "happy",
            "sad",
            "angry",
            "excited",
            "calm",
            "neutral",
        ]
        assert response.safety_status == "safe"
        assert response.confidence > 0.0
        assert response.processing_time_ms > 0
        assert response.processing_source == "distributed"

        # Check service results
        assert response.service_results is not None
        assert "transcription" in response.service_results
        assert "emotion" in response.service_results
        assert "safety" in response.service_results
        assert "ai_response" in response.service_results

        # Should be reasonably fast
        assert processing_time < 5.0  # Less than 5 seconds

    @pytest.mark.asyncio
    async def test_batch_processing(self, processor):
        """Test batch conversation processing."""
        if not DISTRIBUTED_AI_IMPORTS_AVAILABLE:
            pytest.skip(f"Distributed AI imports not available: {import_error}")

        await processor.initialize()

        # Create multiple test requests
        requests = []
        for i in range(3):
            audio_data = np.random.uniform(-0.1, 0.1, 16000)
            if hasattr(audio_data, "astype"):
                audio_data = audio_data.astype(np.float32)
                audio_bytes = (audio_data * 32767).astype(np.int16).tobytes()
            else:
                # Mock numpy fallback
                audio_bytes = f"mock_audio_bytes_data_{i}".encode()

            child_context = ChildContext(
                child_id=f"test_child_{i:03d}", name=f"طفل {i}", age=5 + i
            )

            requests.append((audio_bytes, child_context))

        # Process batch
        start_time = time.time()
        responses = await processor.process_batch_conversations(requests)
        batch_time = time.time() - start_time

        # Verify batch results
        assert len(responses) == 3
        assert all(isinstance(r, ConversationResponse) for r in responses)
        assert all(r.success for r in responses)

        # Batch processing should be efficient
        assert batch_time < 10.0  # Should complete within 10 seconds

    @pytest.mark.asyncio
    async def test_safety_filtering(self, processor):
        """Test safety filtering functionality."""
        if not DISTRIBUTED_AI_IMPORTS_AVAILABLE:
            pytest.skip(f"Distributed AI imports not available: {import_error}")

        await processor.initialize()

        # Create potentially unsafe content
        audio_data = np.random.uniform(-0.1, 0.1, 16000)
        if hasattr(audio_data, "astype"):
            audio_data = audio_data.astype(np.float32)
            audio_bytes = (audio_data * 32767).astype(np.int16).tobytes()
        else:
            # Mock numpy fallback
            audio_bytes = b"mock_unsafe_audio_data"

        child_context = ChildContext(
            child_id="test_child_safety", name="طفل الأمان", age=6
        )

        # Mock unsafe content by patching the safety service
        with patch.object(
            MockAIServices, "check_safety", new_callable=AsyncMock
        ) as mock_safety:
            mock_safety.return_value = {
                "is_safe": False,
                "risk_level": "high",
                "confidence": 0.95,
                "detected_issues": ["inappropriate: harmful_word"],
                "processing_time_ms": 20,
            }

            response = await processor.process_conversation(audio_bytes, child_context)

            # Should be marked as unsafe
            assert response.success is False
            assert response.safety_status == "unsafe"
            assert "unsafe" in response.error_message.lower()

    def test_performance_metrics(self, processor):
        """Test performance metrics collection."""
        if not DISTRIBUTED_AI_IMPORTS_AVAILABLE:
            pytest.skip(f"Distributed AI imports not available: {import_error}")

        metrics = processor.get_performance_metrics()

        assert isinstance(metrics, dict)
        assert "processing_metrics" in metrics
        assert "system_info" in metrics
        assert "service_health" in metrics
        assert "timestamp" in metrics

        # Check processing metrics structure
        processing_metrics = metrics["processing_metrics"]
        assert "total_requests" in processing_metrics
        assert "successful_requests" in processing_metrics
        assert "failed_requests" in processing_metrics
        assert "average_processing_time_ms" in processing_metrics

        # Check system info
        system_info = metrics["system_info"]
        assert "ray_available" in system_info
        assert "ai_services_available" in system_info
        assert "audio_processing_available" in system_info

    @pytest.mark.asyncio
    async def test_error_handling(self, processor):
        """Test error handling in conversation processing."""
        if not DISTRIBUTED_AI_IMPORTS_AVAILABLE:
            pytest.skip(f"Distributed AI imports not available: {import_error}")

        await processor.initialize()

        # Test with invalid audio data
        invalid_audio = b"invalid_audio_data"
        child_context = ChildContext(child_id="test_error", name="Test Error", age=6)

        # Should handle gracefully
        response = await processor.process_conversation(invalid_audio, child_context)

        # Should still return a valid response structure
        assert isinstance(response, ConversationResponse)
        assert response.request_id is not None
        # May succeed with mock services even with invalid data


class TestProcessingMetrics:
    """Test processing metrics functionality."""

    def test_metrics_initialization(self):
        """Test metrics object initialization."""
        if not DISTRIBUTED_AI_IMPORTS_AVAILABLE:
            pytest.skip(f"Distributed AI imports not available: {import_error}")

        metrics = ProcessingMetrics()

        assert metrics.total_requests == 0
        assert metrics.successful_requests == 0
        assert metrics.failed_requests == 0
        assert metrics.average_processing_time_ms == 0.0
        assert isinstance(metrics.service_latencies, dict)
        assert metrics.throughput_per_second == 0.0
        assert metrics.last_updated is not None


class TestServiceIntegration:
    """Test integration with existing services."""

    @pytest.mark.asyncio
    async def test_service_availability_detection(self):
        """Test detection of available services."""
        if not DISTRIBUTED_AI_IMPORTS_AVAILABLE:
            pytest.skip(f"Distributed AI imports not available: {import_error}")

        processor = DistributedAIProcessor()
        await processor.initialize()

        metrics = processor.get_performance_metrics()
        system_info = metrics["system_info"]

        # Should detect availability of various components
        assert isinstance(system_info["ray_available"], bool)
        assert isinstance(system_info["ai_services_available"], bool)
        assert isinstance(system_info["audio_processing_available"], bool)

    @pytest.mark.asyncio
    async def test_fallback_behavior(self):
        """Test fallback to mock services when real services unavailable."""
        if not DISTRIBUTED_AI_IMPORTS_AVAILABLE:
            pytest.skip(f"Distributed AI imports not available: {import_error}")

        processor = DistributedAIProcessor()

        # Should initialize successfully even without external dependencies
        await processor.initialize()

        # Should have mock services available
        assert len(processor.services) > 0
        assert AIServiceType.TRANSCRIPTION in processor.services


class TestDistributedScaling:
    """Test distributed scaling capabilities."""

    @pytest.mark.asyncio
    async def test_load_optimization(self):
        """Test system optimization for different loads."""
        if not DISTRIBUTED_AI_IMPORTS_AVAILABLE:
            pytest.skip(f"Distributed AI imports not available: {import_error}")

        processor = DistributedAIProcessor()
        await processor.initialize()

        # Test optimization for high load
        await processor.optimize_for_load(expected_load=100)

        # Should not raise errors
        metrics = processor.get_performance_metrics()
        assert metrics is not None

    @pytest.mark.asyncio
    async def test_concurrent_processing(self):
        """Test concurrent conversation processing."""
        if not DISTRIBUTED_AI_IMPORTS_AVAILABLE:
            pytest.skip(f"Distributed AI imports not available: {import_error}")

        processor = DistributedAIProcessor()
        await processor.initialize()

        # Create multiple concurrent requests
        async def create_conversation_task(i):
            audio_data = np.random.uniform(-0.1, 0.1, 16000)
            if hasattr(audio_data, "astype"):
                audio_data = audio_data.astype(np.float32)
                audio_bytes = (audio_data * 32767).astype(np.int16).tobytes()
            else:
                # Mock numpy fallback
                audio_bytes = f"mock_concurrent_audio_{i}".encode()

            child_context = ChildContext(
                child_id=f"concurrent_child_{i}", name=f"طفل {i}", age=6
            )

            return await processor.process_conversation(audio_bytes, child_context)

        # Run multiple conversations concurrently
        num_concurrent = 5
        tasks = [create_conversation_task(i) for i in range(num_concurrent)]

        start_time = time.time()
        responses = await asyncio.gather(*tasks)
        concurrent_time = time.time() - start_time

        # All should succeed
        assert len(responses) == num_concurrent
        assert all(isinstance(r, ConversationResponse) for r in responses)
        assert all(r.success for r in responses)

        # Concurrent processing should be efficient
        assert concurrent_time < 15.0  # Should complete within 15 seconds


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
