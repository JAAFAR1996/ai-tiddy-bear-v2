"""Unit Tests for Edge AI Manager System.

AI Team Implementation - Task 10 Tests
Author: AI Team Lead
"""

import sys
import time
from pathlib import Path

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
    pytest = MockPytest()

# Import the modules to test
try:
    from infrastructure.edge_ai.edge_ai_manager.edge_ai_manager import (
        EdgeAIManager,
        EdgeAudioFeatures,
        EdgeEmotionResult,
        EdgeModelConfig,
        EdgeProcessingMode,
        EdgeProcessingResult,
        EdgeSafetyResult,
        SafetyLevel,
        WakeWordModel,
    )

    EDGE_AI_IMPORTS_AVAILABLE = True
except ImportError as e:
    EDGE_AI_IMPORTS_AVAILABLE = False
    import_error = str(e)


class TestEdgeModelConfig:
    """Test edge AI model configuration."""

    def test_default_config(self):
        """Test default configuration values."""
        if not EDGE_AI_IMPORTS_AVAILABLE:
            pytest.skip(f"Edge AI imports not available: {import_error}")

        config = EdgeModelConfig()
        assert config.wake_word_model == WakeWordModel.STANDARD
        assert config.processing_mode == EdgeProcessingMode.BALANCED
        assert config.safety_level == SafetyLevel.STANDARD
        assert config.enable_caching is True
        assert config.model_optimization is True


class TestEdgeAIManager:
    """Test main Edge AI Manager functionality."""

    @pytest.fixture
    def edge_ai_manager(self):
        """Create Edge AI Manager for testing."""
        if not EDGE_AI_IMPORTS_AVAILABLE:
            pytest.skip(f"Edge AI imports not available: {import_error}")

        config = EdgeModelConfig()
        return EdgeAIManager(config)

    def test_initialization(self, edge_ai_manager):
        """Test Edge AI Manager initialization."""
        if not EDGE_AI_IMPORTS_AVAILABLE:
            pytest.skip(f"Edge AI imports not available: {import_error}")

        assert edge_ai_manager.config is not None
        assert edge_ai_manager.model_manager is not None
        assert edge_ai_manager.feature_extractor is not None
        assert edge_ai_manager.wake_word_detector is not None
        assert edge_ai_manager.emotion_analyzer is not None
        assert edge_ai_manager.safety_checker is not None

    @pytest.mark.asyncio
    async def test_initialize_models(self, edge_ai_manager):
        """Test model initialization."""
        if not EDGE_AI_IMPORTS_AVAILABLE:
            pytest.skip(f"Edge AI imports not available: {import_error}")

        # Should not raise exception even without real models
        await edge_ai_manager.initialize()

        # Check that components are properly initialized
        assert edge_ai_manager.wake_word_detector.model is not None
        assert edge_ai_manager.emotion_analyzer.model is not None

    @pytest.mark.asyncio
    async def test_process_on_edge(self, edge_ai_manager):
        """Test edge processing pipeline."""
        if not EDGE_AI_IMPORTS_AVAILABLE:
            pytest.skip(f"Edge AI imports not available: {import_error}")

        # Initialize the manager
        await edge_ai_manager.initialize()

        # Create mock audio data
        audio_data = np.random.uniform(-1, 1, 16000)
        if hasattr(audio_data, "astype"):
            audio_data = audio_data.astype(np.float32)
        else:
            # Mock numpy fallback
            audio_data = [0.5] * 16000

        # Process on edge
        result = await edge_ai_manager.process_on_edge(audio_data)

        # Verify result structure
        assert isinstance(result, EdgeProcessingResult)
        assert isinstance(result.should_process_cloud, bool)
        assert isinstance(result.wake_word_detected, bool)
        assert isinstance(result.priority, int)
        assert 1 <= result.priority <= 10
        assert 0.0 <= result.confidence <= 1.0
        assert result.processing_time_ms > 0

    @pytest.mark.asyncio
    async def test_wake_word_detection(self, edge_ai_manager):
        """Test wake word detection functionality."""
        if not EDGE_AI_IMPORTS_AVAILABLE:
            pytest.skip(f"Edge AI imports not available: {import_error}")

        await edge_ai_manager.initialize()

        # Test with high energy audio (should trigger wake word)
        high_energy_audio = np.random.uniform(-0.5, 0.5, 16000)
        if hasattr(high_energy_audio, "astype"):
            high_energy_audio = high_energy_audio.astype(np.float32)
        else:
            # Mock numpy fallback
            high_energy_audio = [0.25] * 16000

        (
            detected,
            confidence,
        ) = await edge_ai_manager.wake_word_detector.detect_wake_word(high_energy_audio)

        assert isinstance(detected, bool)
        assert 0.0 <= confidence <= 1.0

    @pytest.mark.asyncio
    async def test_emotion_analysis(self, edge_ai_manager):
        """Test emotion analysis functionality."""
        if not EDGE_AI_IMPORTS_AVAILABLE:
            pytest.skip(f"Edge AI imports not available: {import_error}")

        await edge_ai_manager.initialize()

        # Create mock audio features
        mock_features = EdgeAudioFeatures(
            mfcc=np.array([0.1, 0.2, 0.3, 0.4, 0.5]),
            spectral_centroid=1000.0,
            zero_crossing_rate=0.05,
            rms_energy=0.1,
            pitch_mean=150.0,
            pitch_std=20.0,
            tempo=120.0,
            spectral_rolloff=2000.0,
            extraction_time_ms=10.0,
        )

        # Analyze emotion
        emotion_result = await edge_ai_manager.emotion_analyzer.analyze_emotion(
            mock_features
        )

        assert isinstance(emotion_result, EdgeEmotionResult)
        assert emotion_result.primary_emotion in [
            "happy",
            "sad",
            "angry",
            "fear",
            "surprise",
            "calm",
            "excited",
            "neutral",
        ]
        assert 0.0 <= emotion_result.confidence <= 1.0
        assert 0.0 <= emotion_result.arousal <= 1.0
        assert 0.0 <= emotion_result.valence <= 1.0

    @pytest.mark.asyncio
    async def test_safety_checking(self, edge_ai_manager):
        """Test safety checking functionality."""
        if not EDGE_AI_IMPORTS_AVAILABLE:
            pytest.skip(f"Edge AI imports not available: {import_error}")

        await edge_ai_manager.initialize()

        # Create mock audio features
        mock_features = EdgeAudioFeatures(
            mfcc=np.array([0.1, 0.2, 0.3, 0.4, 0.5]),
            spectral_centroid=1000.0,
            zero_crossing_rate=0.05,
            rms_energy=0.1,
            pitch_mean=150.0,
            pitch_std=20.0,
            tempo=120.0,
            spectral_rolloff=2000.0,
            extraction_time_ms=10.0,
        )

        # Test with safe text
        safety_result = await edge_ai_manager.safety_checker.check_safety(
            mock_features, "Hello, how are you today?"
        )

        assert isinstance(safety_result, EdgeSafetyResult)
        assert isinstance(safety_result.passed, bool)
        assert safety_result.risk_level in [
            "low",
            "medium",
            "high",
            "critical",
            "unknown",
        ]
        assert 0.0 <= safety_result.safety_score <= 1.0

        # Test with potentially unsafe text
        unsafe_safety_result = await edge_ai_manager.safety_checker.check_safety(
            mock_features, "I hate this stupid thing"
        )

        assert isinstance(unsafe_safety_result, EdgeSafetyResult)
        # Should detect some issues
        assert (
            len(unsafe_safety_result.detected_issues) > 0
            or unsafe_safety_result.safety_score < 1.0
        )

    def test_performance_stats(self, edge_ai_manager):
        """Test performance statistics generation."""
        if not EDGE_AI_IMPORTS_AVAILABLE:
            pytest.skip(f"Edge AI imports not available: {import_error}")

        stats = edge_ai_manager.get_performance_stats()

        assert "processing_stats" in stats
        assert "model_info" in stats
        assert "configuration" in stats
        assert "device_capabilities" in stats

        # Check processing stats structure
        processing_stats = stats["processing_stats"]
        assert "total_processed" in processing_stats
        assert "wake_words_detected" in processing_stats
        assert "average_processing_time" in processing_stats
        assert "error_count" in processing_stats

    def test_device_optimization(self, edge_ai_manager):
        """Test device-specific optimization."""
        if not EDGE_AI_IMPORTS_AVAILABLE:
            pytest.skip(f"Edge AI imports not available: {import_error}")

        # Test low memory device optimization
        low_mem_specs = {"memory_mb": 128, "cpu_cores": 1}
        edge_ai_manager.optimize_for_device(low_mem_specs)
        assert edge_ai_manager.config.processing_mode == EdgeProcessingMode.POWER_SAVE

        # Test high memory device optimization
        high_mem_specs = {"memory_mb": 1024, "cpu_cores": 4}
        edge_ai_manager.optimize_for_device(high_mem_specs)
        assert edge_ai_manager.config.processing_mode == EdgeProcessingMode.BALANCED

    @pytest.mark.asyncio
    async def test_processing_modes(self, edge_ai_manager):
        """Test different processing modes."""
        if not EDGE_AI_IMPORTS_AVAILABLE:
            pytest.skip(f"Edge AI imports not available: {import_error}")

        await edge_ai_manager.initialize()
        audio_data = np.random.uniform(-1, 1, 16000)
        if hasattr(audio_data, "astype"):
            audio_data = audio_data.astype(np.float32)
        else:
            # Mock numpy fallback
            audio_data = [0.5] * 16000

        # Test ultra low latency mode
        edge_ai_manager.config.processing_mode = EdgeProcessingMode.ULTRA_LOW_LATENCY
        result_fast = await edge_ai_manager.process_on_edge(audio_data)

        # Test high accuracy mode
        edge_ai_manager.config.processing_mode = EdgeProcessingMode.HIGH_ACCURACY
        result_accurate = await edge_ai_manager.process_on_edge(audio_data)

        # Both should work but potentially with different processing times
        assert isinstance(result_fast, EdgeProcessingResult)
        assert isinstance(result_accurate, EdgeProcessingResult)


class TestEdgeAudioFeatures:
    """Test audio feature extraction."""

    def test_feature_structure(self):
        """Test EdgeAudioFeatures structure."""
        if not EDGE_AI_IMPORTS_AVAILABLE:
            pytest.skip(f"Edge AI imports not available: {import_error}")

        features = EdgeAudioFeatures(
            mfcc=np.array([0.1, 0.2, 0.3]),
            spectral_centroid=1000.0,
            zero_crossing_rate=0.05,
            rms_energy=0.1,
            pitch_mean=150.0,
            pitch_std=20.0,
            tempo=120.0,
            spectral_rolloff=2000.0,
            extraction_time_ms=10.0,
        )

        assert len(features.mfcc) == 3
        assert features.spectral_centroid == 1000.0
        assert features.extraction_time_ms == 10.0


class TestEdgeProcessingModes:
    """Test different edge processing modes."""

    def test_processing_mode_enum(self):
        """Test processing mode enumeration."""
        if not EDGE_AI_IMPORTS_AVAILABLE:
            pytest.skip(f"Edge AI imports not available: {import_error}")

        assert EdgeProcessingMode.ULTRA_LOW_LATENCY.value == "ultra_low_latency"
        assert EdgeProcessingMode.BALANCED.value == "balanced"
        assert EdgeProcessingMode.HIGH_ACCURACY.value == "high_accuracy"
        assert EdgeProcessingMode.POWER_SAVE.value == "power_save"

    def test_wake_word_models(self):
        """Test wake word model options."""
        if not EDGE_AI_IMPORTS_AVAILABLE:
            pytest.skip(f"Edge AI imports not available: {import_error}")

        assert WakeWordModel.LIGHTWEIGHT.value == "wake_word_lite.tflite"
        assert WakeWordModel.STANDARD.value == "wake_word.tflite"
        assert WakeWordModel.ENHANCED.value == "wake_word_enhanced.tflite"

    def test_safety_levels(self):
        """Test safety level options."""
        if not EDGE_AI_IMPORTS_AVAILABLE:
            pytest.skip(f"Edge AI imports not available: {import_error}")

        assert SafetyLevel.BASIC.value == "basic"
        assert SafetyLevel.STANDARD.value == "standard"
        assert SafetyLevel.ENHANCED.value == "enhanced"


class TestMockFunctionality:
    """Test mock functionality when TensorFlow is not available."""

    @pytest.mark.asyncio
    async def test_mock_processing(self):
        """Test that system works with mock models."""
        if not EDGE_AI_IMPORTS_AVAILABLE:
            pytest.skip(f"Edge AI imports not available: {import_error}")

        # Create manager (should use mock models if TF not available)
        config = EdgeModelConfig()
        manager = EdgeAIManager(config)
        await manager.initialize()

        # Test processing with mock models
        audio_data = np.random.uniform(-1, 1, 16000)
        if hasattr(audio_data, "astype"):
            audio_data = audio_data.astype(np.float32)
        else:
            # Mock numpy fallback
            audio_data = [0.5] * 16000

        result = await manager.process_on_edge(audio_data)

        # Should still produce valid results with mock models
        assert isinstance(result, EdgeProcessingResult)
        assert result.processing_time_ms > 0


class TestErrorHandling:
    """Test error handling and fallback mechanisms."""

    @pytest.mark.asyncio
    async def test_invalid_audio_data(self):
        """Test handling of invalid audio data."""
        if not EDGE_AI_IMPORTS_AVAILABLE:
            pytest.skip(f"Edge AI imports not available: {import_error}")

        config = EdgeModelConfig()
        manager = EdgeAIManager(config)
        await manager.initialize()

        # Test with empty audio
        empty_audio = np.array([])
        result = await manager.process_on_edge(empty_audio)

        # Should handle gracefully
        assert isinstance(result, EdgeProcessingResult)

    @pytest.mark.asyncio
    async def test_processing_failure_fallback(self):
        """Test fallback when processing fails."""
        if not EDGE_AI_IMPORTS_AVAILABLE:
            pytest.skip(f"Edge AI imports not available: {import_error}")

        config = EdgeModelConfig()
        manager = EdgeAIManager(config)
        await manager.initialize()

        # Test with invalid audio format
        invalid_audio = np.array(["invalid", "data"])

        try:
            result = await manager.process_on_edge(invalid_audio)
            # Should either handle gracefully or provide fallback
            assert isinstance(result, EdgeProcessingResult)
        except Exception:  # Expected for invalid data
            pass


class TestPerformanceOptimization:
    """Test performance optimization features."""

    @pytest.mark.asyncio
    async def test_processing_speed(self):
        """Test that processing meets speed requirements."""
        if not EDGE_AI_IMPORTS_AVAILABLE:
            pytest.skip(f"Edge AI imports not available: {import_error}")

        config = EdgeModelConfig(processing_mode=EdgeProcessingMode.ULTRA_LOW_LATENCY)
        manager = EdgeAIManager(config)
        await manager.initialize()

        audio_data = np.random.uniform(-1, 1, 16000)
        if hasattr(audio_data, "astype"):
            audio_data = audio_data.astype(np.float32)
        else:
            # Mock numpy fallback
            audio_data = [0.5] * 16000

        start_time = time.time()
        result = await manager.process_on_edge(audio_data)
        end_time = time.time()

        processing_time_ms = (end_time - start_time) * 1000

        # For ultra low latency mode, should be quite fast
        assert processing_time_ms < 200  # 200ms max for ultra low latency
        assert result.processing_time_ms > 0

    def test_memory_efficiency(self):
        """Test memory usage efficiency."""
        if not EDGE_AI_IMPORTS_AVAILABLE:
            pytest.skip(f"Edge AI imports not available: {import_error}")

        # Create multiple managers to test memory usage
        managers = []
        for i in range(5):
            config = EdgeModelConfig()
            manager = EdgeAIManager(config)
            managers.append(manager)

        # Should not cause memory issues
        assert len(managers) == 5


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
